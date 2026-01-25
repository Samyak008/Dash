"""CSV Parser for broker portfolio files (Zerodha, Upstox)"""
import csv
import io
from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass


@dataclass
class ParsedHolding:
    """Represents a single parsed holding from CSV"""
    ticker_symbol: str
    quantity: Decimal
    average_price: Decimal
    raw_ticker: str  # Original ticker before normalization


class BrokerDetector:
    """Detects which broker the CSV is from based on headers"""
    
    ZERODHA_HEADERS = ["instrument", "qty.", "avg. cost"]
    UPSTOX_HEADERS = ["symbol", "quantity", "buy price"]
    
    @staticmethod
    def detect(headers: List[str]) -> str:
        """Detect broker from CSV headers"""
        headers_lower = [h.lower().strip() for h in headers]
        
        if all(h in headers_lower for h in BrokerDetector.ZERODHA_HEADERS):
            return "zerodha"
        elif all(h in headers_lower for h in BrokerDetector.UPSTOX_HEADERS):
            return "upstox"
        else:
            return "unknown"


class PortfolioCSVParser:
    """Parse portfolio CSV files from various brokers"""
    
    def __init__(self, exchange: str = "NSE"):
        """
        Initialize parser
        
        Args:
            exchange: Default exchange suffix (NSE -> .NS, BSE -> .BO)
        """
        self.exchange_suffix = ".NS" if exchange == "NSE" else ".BO"
    
    def parse(self, file_content: bytes) -> tuple[List[ParsedHolding], List[str]]:
        """
        Parse CSV file content
        
        Returns:
            Tuple of (parsed_holdings, errors)
        """
        try:
            content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            return [], ["Invalid file encoding. Please use UTF-8 encoded CSV."]
        
        reader = csv.DictReader(io.StringIO(content))
        headers = reader.fieldnames or []
        
        broker = BrokerDetector.detect(headers)
        
        if broker == "unknown":
            return [], [f"Unrecognized CSV format. Headers: {', '.join(headers)}"]
        
        # Route to appropriate parser
        if broker == "zerodha":
            return self._parse_zerodha(reader)
        elif broker == "upstox":
            return self._parse_upstox(reader)
        
        return [], ["Unsupported broker"]
    
    def _parse_zerodha(self, reader: csv.DictReader) -> tuple[List[ParsedHolding], List[str]]:
        """Parse Zerodha CSV format"""
        holdings = []
        errors = []
        
        for idx, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
            try:
                raw_ticker = row.get("instrument", "").strip()
                qty_str = row.get("qty.", "0").strip().replace(",", "")
                price_str = row.get("avg. cost", "0").strip().replace(",", "")
                
                if not raw_ticker:
                    continue  # Skip empty rows
                
                # Normalize ticker (add exchange suffix if missing)
                ticker = self._normalize_ticker(raw_ticker)
                
                quantity = Decimal(qty_str)
                avg_price = Decimal(price_str)
                
                if quantity <= 0:
                    errors.append(f"Row {idx}: Quantity must be > 0 for {raw_ticker}")
                    continue
                
                holdings.append(ParsedHolding(
                    ticker_symbol=ticker,
                    quantity=quantity,
                    average_price=avg_price,
                    raw_ticker=raw_ticker
                ))
                
            except (ValueError, InvalidOperation) as e:
                errors.append(f"Row {idx}: Invalid number format - {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return holdings, errors
    
    def _parse_upstox(self, reader: csv.DictReader) -> tuple[List[ParsedHolding], List[str]]:
        """Parse Upstox CSV format"""
        holdings = []
        errors = []
        
        for idx, row in enumerate(reader, start=2):
            try:
                raw_ticker = row.get("symbol", "").strip()
                qty_str = row.get("quantity", "0").strip().replace(",", "")
                price_str = row.get("buy price", "0").strip().replace(",", "")
                
                if not raw_ticker:
                    continue
                
                ticker = self._normalize_ticker(raw_ticker)
                quantity = Decimal(qty_str)
                avg_price = Decimal(price_str)
                
                if quantity <= 0:
                    errors.append(f"Row {idx}: Quantity must be > 0 for {raw_ticker}")
                    continue
                
                holdings.append(ParsedHolding(
                    ticker_symbol=ticker,
                    quantity=quantity,
                    average_price=avg_price,
                    raw_ticker=raw_ticker
                ))
                
            except (ValueError, InvalidOperation) as e:
                errors.append(f"Row {idx}: Invalid number format - {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return holdings, errors
    
    def _normalize_ticker(self, ticker: str) -> str:
        """
        Normalize ticker symbol for Yahoo Finance
        
        Examples:
            RELIANCE -> RELIANCE.NS
            TCS -> TCS.NS
            INFY.BO -> INFY.BO (already has suffix)
        """
        ticker = ticker.strip().upper()
        
        # If already has a suffix, return as-is
        if "." in ticker:
            return ticker
        
        # Add default exchange suffix
        return f"{ticker}{self.exchange_suffix}"
