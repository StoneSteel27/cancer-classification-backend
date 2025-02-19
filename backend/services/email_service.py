from mailjet_rest import Client
from flask import current_app
import logging
from datetime import datetime
import os


class EmailService:
    _client = None

    @classmethod
    def get_mailjet_client(cls):
        """Gets or creates Mailjet API client."""
        try:
            if cls._client is None:
                api_key = os.getenv('MAILJET_API_KEY', '2594ee509bf6648d23b787d9e243ff70')
                api_secret = os.getenv('MAILJET_API_SECRET', '85e083588e5b5fe4433821777a84c94a')
                cls._client = Client(auth=(api_key, api_secret))
            return cls._client
        except Exception as e:
            logging.error(f"Failed to initialize Mailjet client: {str(e)}")
            raise

    @classmethod
    def send_message(cls, to, subject, html_content):
        """Send an email message using Mailjet."""
        try:
            client = cls.get_mailjet_client()
            data = {
                'FromEmail': os.getenv('MAILJET_SENDER', 'contactdrsuzane@gmail.com'),
                'FromName': "Dr. Suzane's Cancer Classification System",
                'Subject': subject,
                'Html-part': html_content,
                'Recipients': [{'Email': to}]
            }

            result = client.send.create(data=data)

            if result.status_code == 200:
                logging.info(f"Email sent successfully to {to}")
                return True
            else:
                logging.error(f"Failed to send email: {result.json()}")
                return False

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
                html_content=html_body
            )

        except Exception as e:
            logging.error(f"Error sending verification email to {email}: {str(e)}")
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
                html_content=html_body
            )

        except Exception as e:
            logging.error(f"Error sending password reset email to {email}: {str(e)}")
            return False
