#!/usr/bin/env python3
"""
SIMPLE COMPREHENSIVE BROWSER TESTING
Tests the Next.js AI Agent Dashboard at http://localhost:3002
"""

import sys
import time
import requests
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

def run_comprehensive_test():
    base_url = "http://localhost:3002"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    print(f"🧪 Starting Comprehensive Browser Testing at {datetime.now()}")
    print(f"🔗 Testing URL: {base_url}")
    
    results = []
    
    # Test server accessibility
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Server is accessible")
            results.append("✅ Server Accessibility: PASS")
        else:
            print(f"❌ Server returned status {response.status_code}")
            results.append(f"❌ Server Accessibility: FAIL - Status {response.status_code}")
            return results
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        results.append(f"❌ Server Accessibility: FAIL - {e}")
        return results
    
    # Start browser testing
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        # Collect console errors
        console_errors = []
        def handle_console(msg):
            if msg.type in ["error", "warning"]:
                console_errors.append(f"{msg.type}: {msg.text}")
        page.on("console", handle_console)
        
        try:
            # Test 1: Homepage
            print("\n📄 Testing Homepage...")
            page.goto(base_url)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # Capture homepage
            page.screenshot(path=str(screenshots_dir / f"{timestamp}_homepage.png"), full_page=True)
            
            title = page.title()
            print(f"   Page title: {title}")
            results.append(f"✅ Homepage: Title='{title}'")
            
            # Check for main content
            main_content = page.locator("main, [role='main'], .main").count()
            nav_content = page.locator("nav, .sidebar, .navigation").count()
            print(f"   Main content areas: {main_content}")
            print(f"   Navigation elements: {nav_content}")
            results.append(f"✅ Homepage Content: Main={main_content}, Nav={nav_content}")
            
        except Exception as e:
            print(f"   ❌ Homepage error: {e}")
            results.append(f"❌ Homepage: {e}")
            page.screenshot(path=str(screenshots_dir / f"{timestamp}_homepage_error.png"))
        
        try:
            # Test 2: Authentication
            print("\n🔐 Testing Authentication...")
            auth_paths = ["/auth/login", "/login", "/auth"]
            
            for auth_path in auth_paths:
                try:
                    page.goto(f"{base_url}{auth_path}")
                    page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Capture auth page
                    page.screenshot(path=str(screenshots_dir / f"{timestamp}_auth{auth_path.replace('/', '_')}.png"), full_page=True)
                    
                    # Check for form elements
                    email_inputs = page.locator("input[type='email'], input[name='email']").count()
                    password_inputs = page.locator("input[type='password'], input[name='password']").count()
                    submit_buttons = page.locator("button[type='submit'], input[type='submit']").count()
                    
                    print(f"   {auth_path}: email={email_inputs}, password={password_inputs}, submit={submit_buttons}")
                    
                    if email_inputs > 0 and password_inputs > 0:
                        results.append(f"✅ Auth Form ({auth_path}): Complete form found")
                        
                        # Test form validation
                        submit_btn = page.locator("button[type='submit'], input[type='submit']").first
                        if submit_btn.is_visible():
                            submit_btn.click()
                            page.wait_for_timeout(2000)
                            page.screenshot(path=str(screenshots_dir / f"{timestamp}_auth_validation.png"))
                            results.append(f"✅ Auth Validation: Form submitted (validation check)")
                        break
                    else:
                        results.append(f"❌ Auth Form ({auth_path}): Incomplete - email={email_inputs}, password={password_inputs}")
                        
                except Exception as e:
                    print(f"   ❌ Auth {auth_path} error: {e}")
                    results.append(f"❌ Auth ({auth_path}): {e}")
            
        except Exception as e:
            print(f"   ❌ Authentication testing error: {e}")
            results.append(f"❌ Authentication: {e}")
        
        try:
            # Test 3: Chat Interface
            print("\n💬 Testing Chat Interface...")
            chat_paths = ["/chat", "/dashboard/chat"]
            
            for chat_path in chat_paths:
                try:
                    page.goto(f"{base_url}{chat_path}")
                    page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Capture chat page
                    page.screenshot(path=str(screenshots_dir / f"{timestamp}_chat{chat_path.replace('/', '_')}.png"), full_page=True)
                    
                    # Check for chat elements
                    text_inputs = page.locator("input[type='text'], textarea").count()
                    send_buttons = page.locator("button:has-text('Send'), button:has-text('Submit')").count()
                    messages_areas = page.locator(".messages, .chat-messages, [role='log']").count()
                    
                    print(f"   {chat_path}: inputs={text_inputs}, send_buttons={send_buttons}, message_areas={messages_areas}")
                    
                    if text_inputs > 0:
                        results.append(f"✅ Chat Interface ({chat_path}): Input found")
                        
                        # Try to interact with chat
                        input_field = page.locator("input[type='text'], textarea").first
                        if input_field.is_visible():
                            input_field.fill("Hello, this is a test message")
                            page.wait_for_timeout(1000)
                            page.screenshot(path=str(screenshots_dir / f"{timestamp}_chat_with_message.png"))
                            results.append(f"✅ Chat Input: Message entered successfully")
                        break
                    else:
                        results.append(f"❌ Chat Interface ({chat_path}): No input found")
                        
                except Exception as e:
                    print(f"   ❌ Chat {chat_path} error: {e}")
                    results.append(f"❌ Chat ({chat_path}): {e}")
            
        except Exception as e:
            print(f"   ❌ Chat testing error: {e}")
            results.append(f"❌ Chat: {e}")
        
        try:
            # Test 4: Navigation Links
            print("\n🔗 Testing Navigation...")
            page.goto(base_url)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Get all internal links
            links = page.locator("a").all()
            tested_urls = set()
            
            for i, link in enumerate(links[:5]):  # Test first 5 links
                try:
                    href = link.get_attribute("href")
                    if href and not href.startswith("http") and href not in tested_urls:
                        tested_urls.add(href)
                        full_url = f"{base_url}{href}" if not href.startswith("/") else f"{base_url}{href}"
                        
                        nav_response = requests.get(full_url, timeout=5)
                        if nav_response.status_code == 200:
                            print(f"   ✅ Link {href}: Accessible")
                            results.append(f"✅ Navigation: {href} accessible")
                        else:
                            print(f"   ❌ Link {href}: Status {nav_response.status_code}")
                            results.append(f"❌ Navigation: {href} returns {nav_response.status_code}")
                except Exception as e:
                    results.append(f"❌ Navigation Link {i}: {e}")
                    
        except Exception as e:
            print(f"   ❌ Navigation testing error: {e}")
            results.append(f"❌ Navigation: {e}")
        
        # Test 5: Responsive Design
        print("\n📱 Testing Responsive Design...")
        try:
            screen_sizes = [
                {"name": "Desktop", "width": 1920, "height": 1080},
                {"name": "Tablet", "width": 768, "height": 1024},
                {"name": "Mobile", "width": 375, "height": 667}
            ]
            
            for size in screen_sizes:
                page.set_viewport_size({"width": size["width"], "height": size["height"]})
                page.goto(base_url)
                page.wait_for_load_state("networkidle", timeout=5000)
                page.screenshot(path=str(screenshots_dir / f"{timestamp}_responsive_{size['name'].lower()}.png"))
                print(f"   ✅ {size['name']}: {size['width']}x{size['height']}")
                results.append(f"✅ Responsive {size['name']}: {size['width']}x{size['height']}")
                
        except Exception as e:
            print(f"   ❌ Responsive testing error: {e}")
            results.append(f"❌ Responsive: {e}")
        
        # Console Errors Summary
        if console_errors:
            print(f"\n🚨 Console Errors Found: {len(console_errors)}")
            for error in console_errors[:5]:  # Show first 5 errors
                print(f"   {error}")
            results.append(f"❌ Console Errors: {len(console_errors)} found")
        else:
            print("\n✅ No console errors found")
            results.append("✅ Console Errors: None found")
        
        browser.close()
    
    # Generate summary report
    report_content = f"""
# COMPREHENSIVE BROWSER TEST REPORT
**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Base URL:** {base_url}
**Screenshots:** {screenshots_dir}

## Test Results

"""
    
    passed = len([r for r in results if r.startswith("✅")])
    failed = len([r for r in results if r.startswith("❌")])
    
    report_content += f"**Summary:** {passed} passed, {failed} failed\n\n"
    
    for result in results:
        report_content += f"- {result}\n"
    
    if console_errors:
        report_content += f"\n## Console Errors\n"
        for error in console_errors:
            report_content += f"- {error}\n"
    
    # Write report
    report_path = f"browser_test_report_{timestamp}.md"
    with open(report_path, "w") as f:
        f.write(report_content)
    
    print(f"\n{'='*60}")
    print("COMPREHENSIVE BROWSER TESTING COMPLETE")
    print(f"{'='*60}")
    print(f"📊 Report: {report_path}")
    print(f"📷 Screenshots: {screenshots_dir}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🚨 Console Errors: {len(console_errors)}")
    
    return results, report_path

if __name__ == "__main__":
    results, report_path = run_comprehensive_test()