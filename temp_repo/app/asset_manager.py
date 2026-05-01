import os

def get_flat_assets():
    """Stub for asset_manager to unblock application startup."""
    assets_dir = "/app/assets"
    assets = []
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4')):
                    assets.append(os.path.join(root, file))
    return assets
