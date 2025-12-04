"""
Flask CLI commands for administrative tasks
"""
import click
from flask import Flask
from app import db
from app.models import User


def register_commands(app: Flask):
    """Register CLI commands with the Flask app"""

    @app.cli.command('create-admin')
    @click.option('--email', prompt=True, help='Admin email address')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
    @click.option('--name', prompt=True, help='Admin name')
    def create_admin(email, password, name):
        """Create an admin user"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f'Error: User with email {email} already exists!')
            return

        # Create new admin user
        user = User(
            email=email,
            name=name,
            is_admin=True,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        click.echo(f'Admin user created successfully!')
        click.echo(f'Email: {email}')
        click.echo(f'Name: {name}')

    @app.cli.command('list-users')
    def list_users():
        """List all users"""
        users = User.query.all()
        if not users:
            click.echo('No users found.')
            return

        click.echo(f'\nFound {len(users)} user(s):')
        click.echo('-' * 80)
        for user in users:
            status = '✓ Active' if user.is_active else '✗ Inactive'
            admin = '(Admin)' if user.is_admin else ''
            click.echo(f'{user.email:30s} | {user.name:20s} | {status} {admin}')
        click.echo('-' * 80)
