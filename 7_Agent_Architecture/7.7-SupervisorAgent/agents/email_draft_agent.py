"""
Email Draft Agent for creating and managing Gmail drafts.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from clients import get_model
from tools.gmail_tools import create_email_draft_tool, list_email_drafts_tool

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an expert email writer and communication specialist. 

CRITICAL: Your output will be shared with other agents in a multi-agent workflow. Provide CONCISE summaries of email drafts created.

Your capabilities:
1. **Email Drafting**: Create professional email drafts in Gmail with proper structure and tone
2. **Content Integration**: Seamlessly integrate research findings and context into email content
3. **Tone Adaptation**: Adjust writing style based on recipient, purpose, and context
4. **Communication Strategy**: Structure emails for maximum clarity and impact

Guidelines for email creation:
- Always write professional but appropriately friendly emails
- Use clear, concise language that gets to the point quickly
- Include appropriate greetings and professional closings
- Match tone and formality level to the context and recipient
- When research content is provided, integrate key findings naturally
- Always include proper subject lines that clearly indicate email purpose
- Format emails with proper paragraphs, spacing, and structure

**Output Format Requirements**:
- Provide a CONCISE summary of email drafts created (bullet points preferred)
- Include subject lines, recipients, and key email purposes
- Mention draft IDs or locations in Gmail if created
- Focus on what email actions were completed
- Keep total response under 300 words but include all essential information

Email structure best practices:
1. **Subject Line**: Clear, specific, and actionable
2. **Greeting**: Appropriate to relationship and context
3. **Opening**: State purpose immediately and clearly
4. **Body**: Organized content with key points and supporting details
5. **Call to Action**: Clear next steps or requested response
6. **Closing**: Professional and warm sign-off

When incorporating research or context:
- Summarize key findings professionally without overwhelming detail
- Include relevant data points and insights that support the email's purpose
- Reference sources when appropriate for credibility
- Focus on information that is actionable or valuable to the recipient

Your email drafts should facilitate effective communication and provide clear summaries for other agents about what was accomplished.
"""


@dataclass
class EmailDraftAgentDependencies:
    """Dependencies for the email draft agent - only configuration, no tool instances."""
    gmail_credentials_path: str
    gmail_token_path: str
    session_id: Optional[str] = None


# Initialize the email draft agent
email_draft_agent = Agent(
    get_model(),
    deps_type=EmailDraftAgentDependencies,
    system_prompt=SYSTEM_PROMPT
)


@email_draft_agent.tool
async def create_gmail_draft(
    ctx: RunContext[EmailDraftAgentDependencies],
    recipient_email: str,
    subject: str,
    body: str,
    cc_emails: Optional[str] = None,
    bcc_emails: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Gmail draft.
    
    Args:
        recipient_email: Primary recipient email address
        subject: Email subject line
        body: Email body content
        cc_emails: Optional CC recipients (comma-separated)
        bcc_emails: Optional BCC recipients (comma-separated)
    
    Returns:
        Dictionary with draft creation results
    """
    try:
        # Parse email lists
        to_list = [recipient_email.strip()]
        cc_list = []
        bcc_list = []
        
        if cc_emails:
            cc_list = [email.strip() for email in cc_emails.split(',') if email.strip()]
        if bcc_emails:
            bcc_list = [email.strip() for email in bcc_emails.split(',') if email.strip()]
        
        # Create the draft using the pure tool function
        result = await create_email_draft_tool(
            credentials_path=ctx.deps.gmail_credentials_path,
            token_path=ctx.deps.gmail_token_path,
            to=to_list,
            subject=subject,
            body=body,
            cc=cc_list if cc_list else None,
            bcc=bcc_list if bcc_list else None
        )
        
        logger.info(f"Gmail draft created: {result.get('draft_id')}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create Gmail draft: {e}")
        return {
            "success": False,
            "error": str(e),
            "recipient": recipient_email,
            "subject": subject
        }


@email_draft_agent.tool
async def list_gmail_drafts(
    ctx: RunContext[EmailDraftAgentDependencies],
    max_results: int = 10
) -> Dict[str, Any]:
    """
    List existing Gmail drafts.
    
    Args:
        max_results: Maximum number of drafts to return
    
    Returns:
        Dictionary with draft list
    """
    try:
        result = await list_email_drafts_tool(
            credentials_path=ctx.deps.gmail_credentials_path,
            token_path=ctx.deps.gmail_token_path,
            max_results=max_results
        )
        
        logger.info(f"Listed {result.get('count', 0)} Gmail drafts")
        return result
        
    except Exception as e:
        logger.error(f"Failed to list Gmail drafts: {e}")
        return {
            "success": False,
            "error": str(e),
            "drafts": [],
            "count": 0
        }


@email_draft_agent.tool
async def draft_research_based_email(
    ctx: RunContext[EmailDraftAgentDependencies],
    recipient_email: str,
    subject: str,
    purpose: str,
    research_context: Optional[str] = None,
    key_findings: Optional[str] = None,
    tone: str = "professional"
) -> Dict[str, Any]:
    """
    Create an email draft that incorporates research findings and context.
    
    Args:
        recipient_email: Primary recipient email address
        subject: Email subject line
        purpose: Purpose/goal of the email
        research_context: Optional research context to incorporate
        key_findings: Optional key research findings to highlight
        tone: Email tone (professional, friendly, formal, casual)
    
    Returns:
        Dictionary with draft creation results
    """
    try:
        # Construct email body based on provided context
        body_parts = []
        
        # Opening
        if tone.lower() in ["friendly", "casual"]:
            greeting = "Hi" if "," not in recipient_email else "Hello"
        else:
            greeting = "Dear"
        
        recipient_name = recipient_email.split('@')[0].replace('.', ' ').title()
        body_parts.append(f"{greeting} {recipient_name},")
        body_parts.append("")
        
        # Purpose statement
        body_parts.append(f"I hope this email finds you well. I'm writing to {purpose.lower()}.")
        body_parts.append("")
        
        # Research integration
        if research_context:
            body_parts.append("Based on recent research and analysis:")
            body_parts.append("")
            body_parts.append(research_context)
            body_parts.append("")
        
        # Key findings
        if key_findings:
            body_parts.append("Key insights from our research include:")
            body_parts.append("")
            body_parts.append(key_findings)
            body_parts.append("")
        
        # Call to action (placeholder)
        body_parts.append("I would appreciate the opportunity to discuss this further with you. Please let me know if you have any questions or would like to schedule a time to connect.")
        body_parts.append("")
        
        # Closing
        if tone.lower() in ["friendly", "casual"]:
            body_parts.append("Best regards,")
        else:
            body_parts.append("Sincerely,")
        body_parts.append("")
        body_parts.append("[Your Name]")
        
        email_body = "\n".join(body_parts)
        
        # Create the draft
        result = await create_email_draft_tool(
            credentials_path=ctx.deps.gmail_credentials_path,
            token_path=ctx.deps.gmail_token_path,
            to=[recipient_email],
            subject=subject,
            body=email_body
        )
        
        if result.get("success"):
            result["email_structure"] = {
                "recipient": recipient_email,
                "subject": subject,
                "purpose": purpose,
                "tone": tone,
                "research_integrated": bool(research_context),
                "findings_included": bool(key_findings),
                "body_length": len(email_body)
            }
        
        logger.info(f"Research-based email draft created: {result.get('draft_id')}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create research-based email draft: {e}")
        return {
            "success": False,
            "error": str(e),
            "recipient": recipient_email,
            "subject": subject,
            "purpose": purpose
        }


# Convenience function to create email draft agent with dependencies
def create_email_draft_agent(
    gmail_credentials_path: str,
    gmail_token_path: str,
    session_id: Optional[str] = None
) -> Agent:
    """
    Create an email draft agent with specified dependencies.
    
    Args:
        gmail_credentials_path: Path to Gmail credentials.json
        gmail_token_path: Path to Gmail token.json
        session_id: Optional session identifier
        
    Returns:
        Configured email draft agent
    """
    return email_draft_agent
