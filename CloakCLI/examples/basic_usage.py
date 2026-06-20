"""CloakCLI SDK basic usage example."""
import asyncio
from cloakcli import CloakBrowserManagerClient, ConfigLoader

async def main():
    # Load config from environment or config file
    config = ConfigLoader().load()
    client = CloakBrowserManagerClient.from_config(config)

    # List profiles
    profiles = client.profiles.list()
    print(f"Found {len(profiles)} profiles")

    if not profiles:
        # Create one
        profile = client.profiles.create(name="test-profile", humanize=True)
        print(f"Created profile: {profile.id}")
    else:
        profile = profiles[0]

    # Launch browser
    if profile.status != "running":
        client.launch(profile.id)
        print(f"Launched: {profile.id}")

    # Connect via CDP with humanize
    browser = await client.connect(profile.id)
    try:
        page = browser.contexts[0].pages[0]
        await page.goto("https://example.com")
        print(f"Page title: {await page.title()}")
        await page.screenshot(path="example.png")
        print("Screenshot saved: example.png")
    finally:
        await browser.close()

    # Or use convenience methods
    await client.run.open(profile.id, "https://httpbin.org/ip")
    text = await client.run.get_text(profile.id, "body")
    print(text)

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
