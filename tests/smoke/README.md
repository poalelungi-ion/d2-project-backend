# Smoke scripts

Manual checks that exercise the upload endpoints against a **running** backend.
They are deliberately not named `test_*.py`: they issue real HTTP requests at
import time, so pytest would fire them during collection.

Start the API, then run one directly:

```bash
python tests/smoke/upload_confirm.py
python tests/smoke/upload_csv.py      # needs: pip install requests
```

Point them at another instance with `SMOKE_BASE_URL=https://host:port`.
