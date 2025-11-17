import re
from playwright.sync_api import Page, expect

def test_homepage_has_title_and_links(page: Page):
    page.goto("/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("WindFlag"))

    # Expect the page to have a link to the challenges page.
    challenges_link = page.get_by_role("link", name="Challenges")
    expect(challenges_link).to_be_visible()

    # Expect the page to have a link to the scoreboard page.
    scoreboard_link = page.get_by_role("link", name="Scoreboard")
    expect(scoreboard_link).to_be_visible()

    # Expect the page to have a link to the login page.
    login_link = page.get_by_role("link", name="Login")
    expect(login_link).to_be_visible()

    # Expect the page to have a link to the register page.
    register_link = page.get_by_role("link", name="Register")
    expect(register_link).to_be_visible()
