"""
FishingFriend - Root Application Launcher
Delegates directly to FishingFriend/app.py
"""
import os
import sys

# Add FishingFriend directory to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
ff_dir = os.path.join(base_dir, "FishingFriend")
if ff_dir not in sys.path:
    sys.path.insert(0, ff_dir)

# Execute FishingFriend/app.py
app_path = os.path.join(ff_dir, "app.py")
with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

globals()["__file__"] = app_path
exec(compile(code, app_path, "exec"), globals())
