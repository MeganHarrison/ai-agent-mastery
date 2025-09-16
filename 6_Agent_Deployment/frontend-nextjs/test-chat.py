#!/usr/bin/env python3
"""
Test script to automate the Next.js chat application and demonstrate functionality
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_chat_application():
    """Test the Next.js chat application end-to-end"""
    
    async with async_playwright() as p:
        # Launch browser in headful mode to see what's happening
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            print("🌐 Opening Next.js application...")
            await page.goto("http://localhost:3005")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)  # Give it time to render
            
            print("📸 Taking screenshot of initial page...")
            await page.screenshot(path="initial_page.png", full_page=True)
            
            # Check if we're on login/auth page
            if await page.locator("text=Sign in").is_visible():
                print("🔐 Found login page. Looking for auth options...")
                
                # Look for email input or Google sign in
                if await page.locator("input[type='email']").is_visible():
                    print("📧 Found email input, attempting to fill...")
                    await page.fill("input[type='email']", "test@example.com")
                    
                    if await page.locator("input[type='password']").is_visible():
                        await page.fill("input[type='password']", "testpassword")
                    
                    # Look for sign in button
                    if await page.locator("button[type='submit']").is_visible():
                        await page.click("button[type='submit']")
                        await page.wait_for_load_state("networkidle")
                
                # Try Google Sign In if available
                elif await page.locator("text=Continue with Google").is_visible():
                    print("📧 Found Google sign in option...")
                    await page.click("text=Continue with Google")
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                
                # Or try magic link if available
                elif await page.locator("text=Send magic link").is_visible():
                    print("🪄 Found magic link option...")
                    if await page.locator("input[type='email']").is_visible():
                        await page.fill("input[type='email']", "test@example.com")
                        await page.click("text=Send magic link")
                        await asyncio.sleep(2)
            
            # Check if we need to handle any modals or overlays
            if await page.locator("[role='dialog']").is_visible():
                print("📋 Found dialog/modal, attempting to close...")
                if await page.locator("button[aria-label='Close']").is_visible():
                    await page.click("button[aria-label='Close']")
                elif await page.locator("text=✕").is_visible():
                    await page.click("text=✕")
                elif await page.locator("[data-testid='close-button']").is_visible():
                    await page.click("[data-testid='close-button']")
                await asyncio.sleep(1)
            
            print("🔍 Looking for chat interface...")
            
            # Look for common chat interface elements
            chat_input_selectors = [
                "textarea[placeholder*='message']",
                "input[placeholder*='message']", 
                "textarea[placeholder*='type']",
                "input[placeholder*='type']",
                "[data-testid='chat-input']",
                "[data-testid='message-input']",
                "textarea",
                "input[type='text']:not([type='email']):not([type='password'])"
            ]
            
            chat_input = None
            for selector in chat_input_selectors:
                if await page.locator(selector).is_visible():
                    chat_input = page.locator(selector)
                    print(f"✅ Found chat input with selector: {selector}")
                    break
            
            if not chat_input:
                print("❌ Could not find chat input. Taking screenshot for debugging...")
                await page.screenshot(path="no_chat_input.png", full_page=True)
                
                # Print page content for debugging
                title = await page.title()
                url = page.url
                print(f"📄 Page title: {title}")
                print(f"🔗 Current URL: {url}")
                
                # Print all interactive elements
                buttons = await page.locator("button").all()
                inputs = await page.locator("input").all()
                textareas = await page.locator("textarea").all()
                
                print(f"🔘 Found {len(buttons)} buttons")
                print(f"📝 Found {len(inputs)} inputs") 
                print(f"📄 Found {len(textareas)} textareas")
                
                return False
            
            print("💬 Found chat interface! Sending test message...")
            
            # Send a test message about FM Global 8-34
            test_message = "What is FM Global 8-34 about? Please provide an overview of the document and its purpose."
            
            await chat_input.fill(test_message)
            await asyncio.sleep(1)
            
            # Look for send button
            send_button_selectors = [
                "button[type='submit']",
                "button[aria-label*='Send']",
                "[data-testid='send-button']",
                "button:has-text('Send')",
                "button svg[aria-hidden='true']", # Icon buttons
            ]
            
            sent = False
            for selector in send_button_selectors:
                if await page.locator(selector).is_visible():
                    await page.click(selector)
                    print(f"📨 Clicked send button: {selector}")
                    sent = True
                    break
            
            if not sent:
                # Try pressing Enter
                await chat_input.press("Enter")
                print("⌨️ Pressed Enter to send message")
            
            print("⏳ Waiting for AI response...")
            
            # Wait for response - look for new message elements
            response_selectors = [
                "[data-role='assistant']",
                "[data-author='assistant']", 
                ".message.assistant",
                "[role='article']",
                ".ai-message",
                ".bot-message",
                "[data-testid='ai-message']"
            ]
            
            response_found = False
            for i in range(30):  # Wait up to 30 seconds
                for selector in response_selectors:
                    if await page.locator(selector).count() > 0:
                        print(f"✅ Found AI response with selector: {selector}")
                        response_found = True
                        break
                
                if response_found:
                    break
                    
                await asyncio.sleep(1)
                print(f"⏳ Waiting... ({i+1}/30)")
            
            if not response_found:
                print("❌ No AI response found. Checking for any new content...")
                await page.screenshot(path="no_response.png", full_page=True)
                
                # Look for any message elements that appeared after sending
                messages = await page.locator("[data-testid*='message'], .message, [role='article']").all()
                if len(messages) > 1:  # More than just our input
                    print(f"📨 Found {len(messages)} total messages")
                    response_found = True
                
            if response_found:
                print("🎉 SUCCESS! Chat is working. Extracting response...")
                
                # Take screenshot of the conversation
                await page.screenshot(path="chat_success.png", full_page=True)
                
                # Extract the AI response text
                response_text = ""
                for selector in response_selectors + ["[data-testid*='message']", ".message", "[role='article']"]:
                    elements = await page.locator(selector).all()
                    for element in elements:
                        try:
                            text = await element.inner_text()
                            if text and text != test_message and len(text) > 50:  # Skip our input message
                                response_text = text
                                break
                        except:
                            continue
                    if response_text:
                        break
                
                # If no specific response found, get all text from chat area
                if not response_text:
                    chat_area_selectors = [
                        "[data-testid='chat-area']",
                        "[data-testid='messages']", 
                        ".chat-messages",
                        ".conversation",
                        "main"
                    ]
                    
                    for selector in chat_area_selectors:
                        if await page.locator(selector).is_visible():
                            response_text = await page.locator(selector).inner_text()
                            break
                
                print("\n" + "="*80)
                print("🤖 AI AGENT RESPONSE:")
                print("="*80)
                print(response_text[-2000:])  # Last 2000 chars to avoid too much output
                print("="*80)
                
                return True
            
            else:
                print("❌ FAILED: No AI response received")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            await page.screenshot(path="error.png", full_page=True)
            return False
            
        finally:
            print("🔄 Keeping browser open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)
            await browser.close()

if __name__ == "__main__":
    print("🚀 Starting Next.js chat application test...")
    success = asyncio.run(test_chat_application())
    
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")