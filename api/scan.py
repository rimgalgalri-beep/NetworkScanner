"""
Vercel Serverless Function for Network Scanner
Endpoint: /api/scan
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_scanner import NetworkScanner


def handler(request):
    """Handle HTTP requests for network scanning."""
    
    # Check if Supabase credentials are set
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    use_supabase = bool(supabase_url and supabase_key)
    
    try:
        # Initialize scanner
        scanner = NetworkScanner(use_supabase=use_supabase)
        backend = "Supabase" if use_supabase else "SQLite"
        
        # Run scan
        scanner.scan_network()
        
        # Save to database
        if scanner.devices:
            scanner.save_to_database()
            devices_count = len(scanner.devices)
        else:
            devices_count = 0
        
        # Get all devices from database
        all_devices = scanner.get_all_devices()
        
        # Prepare response
        response = {
            "success": True,
            "backend": backend,
            "scanned_devices": devices_count,
            "total_devices": len(all_devices),
            "timestamp": datetime.now().isoformat(),
            "devices": all_devices[:20]  # Return last 20 devices
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response, indent=2)
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        }
