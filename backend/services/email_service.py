import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from flask import current_app
import logging
from datetime import datetime


class EmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    _service = None

    @classmethod
    def get_gmail_service(cls):
        """Gets or creates Gmail API service."""
        try:
            if cls._service:
                return cls._service

            creds = None
            token_file = current_app.config['GMAIL_TOKEN_FILE']

            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        current_app.config['GMAIL_CREDENTIALS_FILE'],
                        cls.SCOPES
                    )
                    creds = flow.run_local_server(port=8080)

                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            cls._service = build('gmail', 'v1', credentials=creds)
            return cls._service
        except Exception as e:
            logging.error(f"Failed to initialize Gmail service: {str(e)}")
            raise

    @classmethod
    def create_message(cls, to, subject, message_text):
        """Create a message for an email."""
        message = MIMEText(message_text, 'html')
        message['to'] = to
        message['from'] = current_app.config['GMAIL_SENDER']
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    @classmethod
    def send_message(cls, to, subject, message_text):
        """Send an email message."""
        try:
            service = cls.get_gmail_service()
            message = cls.create_message(to, subject, message_text)
            sent_message = service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            logging.info(f"Message Id: {sent_message['id']}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False

    @classmethod
    def send_verification_email(cls, email, token):
        if not token:
            logging.error("No token provided for email verification")
            return False

        try:
            verification_link = f"{current_app.config.get('FRONTEND_URL')}/verify/{token}"
            current_year = datetime.now().year

            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <!-- Header Section -->
                        <div style="text-align: center; padding: 20px; border-bottom: 2px solid #f4f4f4;">
                            <h1 style="color: #0055aa; margin-bottom: 10px;">Welcome to Cancer Classification System</h1>
                            <p style="color: #666; font-size: 16px;">Your Advanced Medical Imaging Analysis Platform</p>
                        </div>

                        <!-- Main Content -->
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h2 style="color: #333; margin-bottom: 15px;">One Last Step!</h2>
                            <p style="color: #666; line-height: 1.6;">
                                To ensure secure access and protect your data, please verify your email address by clicking 
                                the button below:
                            </p>

                            <!-- Verification Button -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{verification_link}" 
                                   style="background-color: #0055aa; color: white; padding: 12px 30px; 
                                          text-decoration: none; border-radius: 5px; font-weight: bold;
                                          display: inline-block;">
                                    Verify Email Address
                                </a>
                            </div>

                            <!-- Alternative Link -->
                            <div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 20px;">
                                <p style="color: #666; font-size: 14px; margin: 0;">
                                    If the button doesn't work, copy and paste this link in your browser:
                                    <br>
                                    <span style="color: #0055aa; word-break: break-all;">{verification_link}</span>
                                </p>
                            </div>
                        </div>

                        <!-- Features Section -->
                        <div style="margin-top: 30px; padding: 20px; background-color: #fff;">
                            <h3 style="color: #333; margin-bottom: 15px;">What You Can Do With Our Platform:</h3>
                            <ul style="color: #666; line-height: 1.6; padding-left: 20px;">
                                <li>Upload and analyze medical images</li>
                                <li>Get instant classification results</li>
                                <li>Track your prediction history</li>
                                <li>Access detailed analysis reports</li>
                            </ul>
                        </div>

                        <!-- Security Notice -->
                        <div style="margin-top: 30px; padding: 15px; background-color: #fff4e5; border-radius: 5px;">
                            <p style="color: #666; font-size: 14px; margin: 0;">
                                <strong>Important Security Notice:</strong>
                                <br>
                                • This verification link will expire in 24 hours
                                <br>
                                • If you didn't create this account, please ignore this email
                                <br>
                                • Never share your login credentials with anyone
                            </p>
                        </div>

                        <!-- Footer -->
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                            <p style="color: #999; font-size: 12px;">
                                © {current_year} Cancer Classification System. All rights reserved.
                                <br>
                                This is an automated message, please do not reply.
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """

            return cls.send_message(
                to=email,
                subject="Verify Your Email - Cancer Classification System",
                message_text=html_body
            )


        except Exception as e:
            logging.error(f"Error sending password reset email to {email}: {str(e)}")
            return False

    @classmethod
    def send_reset_email(cls, email, token):
        if not token:
            logging.error("No token provided for password reset")
            return False

        try:
            reset_link = f"{current_app.config.get('FRONTEND_URL')}/reset-password/{token}"

            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
                        <div style="text-align: center; padding: 20px;">
                            <h1 style="color: #0055aa;">Password Reset Request</h1>
                        </div>

                        <div style="padding: 20px;">
                            <p style="color: #666; line-height: 1.6;">
                                We received a request to reset your password. Click the button below to create a new password:
                            </p>

                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{reset_link}" 
                                   style="background-color: #0055aa; color: white; padding: 12px 30px; 
                                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                                    Reset Password
                                </a>
                            </div>

                            <p style="color: #666; font-size: 14px;">
                                If you didn't request this password reset, please ignore this email.
                                <br>
                                This link will expire in 1 hour for security reasons.
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """

            return cls.send_message(
                to=email,
                subject="Reset Your Password - Cancer Classification System",
                message_text=html_body
            )

        except Exception as e:
            logging.error(f"Error sending password reset email to {email}: {str(e)}")
            return False
