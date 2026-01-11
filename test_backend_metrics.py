#!/usr/bin/env python3
"""Quick test to check if metrics are being collected"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

try:
    from client.structured_logging import get_metrics_collector
    from client.dashboard import get_dashboard
    
    print("\n" + "=" * 60)
    print("🧪 METRICS COLLECTION TEST")
    print("=" * 60)
    
    # Get metrics collector
    collector = get_metrics_collector()
    all_metrics = collector.get_all_metrics()
    
    print("\n📊 Counters:")
    if all_metrics['counters']:
        for key, value in all_metrics['counters'].items():
            print(f"  {key}: {value}")
    else:
        print("  ⚠️  No counters collected yet")
    
    print("\n📈 Metrics:")
    if all_metrics['metrics']:
        for key, value in all_metrics['metrics'].items():
            print(f"  {key}: {len(value)} data points")
    else:
        print("  ⚠️  No metrics collected yet")
    
    # Get dashboard data
    print("\n" + "=" * 60)
    print("📊 DASHBOARD DATA")
    print("=" * 60)
    
    dashboard = get_dashboard()
    dashboard_data = dashboard.get_full_dashboard()
    
    # Print full dashboard as JSON
    import json
    print(json.dumps(dashboard_data, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\n💡 Missing modules. Deploy them:")
    print("   cp /mnt/user-data/outputs/client/structured_logging.py client/")
    print("   cp /mnt/user-data/outputs/client/metrics.py client/")
    print("   cp /mnt/user-data/outputs/client/dashboard.py client/")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

