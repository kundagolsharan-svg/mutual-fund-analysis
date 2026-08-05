import os
try:
        import requests  # type: ignore
except Exception:
        # Fallback: minimal requests-like get using urllib if 'requests' is unavailable
        import json
        from urllib import request as _request
        from urllib.error import URLError, HTTPError

        class SimpleResponse:
            def __init__(self, status_code, content):
                self.status_code = status_code
                self._content = content

            def json(self):
                return json.loads(self._content.decode('utf-8'))

            @property
            def content(self):
                return self._content

        class requests:
            @staticmethod
            def get(url, timeout=None):
                try:
                    with _request.urlopen(url, timeout=timeout) as resp:
                        data = resp.read()
                        return SimpleResponse(resp.getcode(), data)
                except HTTPError as e:
                    return SimpleResponse(e.code, getattr(e, 'read', lambda: b'')())
                except URLError as e:
                    raise
except Exception:
    # Fallback: minimal requests-like get using urllib if 'requests' is unavailable
    import json
    from urllib import request as _request
    from urllib.error import URLError, HTTPError

    class SimpleResponse:
        def __init__(self, status_code, content):
            self.status_code = status_code
            self._content = content

        def json(self):
            return json.loads(self._content.decode('utf-8'))

        @property
        def content(self):
            return self._content

    class requests:
        @staticmethod
        def get(url, timeout=None):
            try:
                with _request.urlopen(url, timeout=timeout) as resp:
                    data = resp.read()
                    return SimpleResponse(resp.getcode(), data)
            except HTTPError as e:
                return SimpleResponse(e.code, getattr(e, 'read', lambda: b'')())
            except URLError as e:
                raise
import pandas as pd

# Create output folder if it doesn't exist
output_folder = "data/raw"
os.makedirs(output_folder, exist_ok=True)

# Mutual Fund Schemes
funds = {
    "HDFC_Top_100_Direct": 125497,
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_Large_Cap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

print("=" * 60)
print("Fetching Live NAV Data...")
print("=" * 60)

for fund_name, scheme_code in funds.items():
    url = f"https://api.mfapi.in/mf/{scheme_code}"

    try:
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            json_data = response.json()

            # Extract NAV history
            nav_data = json_data.get("data", [])

            if len(nav_data) == 0:
                print(f"⚠ No NAV data found for {fund_name}")
                continue

            df = pd.DataFrame(nav_data)

            filename = os.path.join(output_folder, f"{fund_name}.csv")
            df.to_csv(filename, index=False)

            print(f"✓ {fund_name} saved successfully")
            print(f"  Records: {len(df)}")
            print(f"  File: {filename}")
            print("-" * 60)

        else:
            print(f"✗ Failed to fetch {fund_name}")
            print(f"HTTP Status Code: {response.status_code}")

    except Exception as e:
        print(f"✗ Error fetching {fund_name}")
        print(e)

print("=" * 60)
print("All downloads completed.")
print("=" * 60)