#!/usr/bin/env python3
"""
Database Management Script
Handles database initialization, migrations, and data management using SQLAlchemy
"""

import os
import sys
import click
from flask import Flask
from flask.cli import with_appcontext
from models.base import db
from models import FeatureMap, FeatureLabel
from config.base import config


def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Use development config by default
    config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Get database URI
    db_config = config[config_name]()
    app.config['SQLALCHEMY_DATABASE_URI'] = db_config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    return app


@click.group()
def cli():
    """Database management commands"""
    pass


@cli.command()
@click.option('--env', default='development', help='Environment (development/production/testing)')
def init_db(env):
    """Initialize database with tables"""
    click.echo(f"🚀 Initializing database for {env} environment...")
    
    # Set environment
    os.environ['FLASK_ENV'] = env
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            click.echo("✅ Database tables created successfully!")
            
            # Show created tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            click.echo(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            click.echo(f"❌ Error initializing database: {e}")
            return 1
    
    return 0


@cli.command()
@click.option('--env', default='development', help='Environment (development/production/testing)')
def drop_db(env):
    """Drop all database tables"""
    if not click.confirm('⚠️  This will DELETE ALL DATA. Are you sure?'):
        click.echo("Cancelled.")
        return
    
    click.echo(f"🗑️  Dropping database tables for {env} environment...")
    
    # Set environment
    os.environ['FLASK_ENV'] = env
    
    app = create_app()
    
    with app.app_context():
        try:
            db.drop_all()
            click.echo("✅ Database tables dropped successfully!")
            
        except Exception as e:
            click.echo(f"❌ Error dropping database: {e}")
            return 1
    
    return 0


@cli.command()
@click.option('--env', default='development', help='Environment (development/production/testing)')
def reset_db(env):
    """Drop and recreate database tables"""
    if not click.confirm('⚠️  This will DELETE ALL DATA and recreate tables. Are you sure?'):
        click.echo("Cancelled.")
        return
    
    click.echo(f"🔄 Resetting database for {env} environment...")
    
    # Set environment
    os.environ['FLASK_ENV'] = env
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            click.echo("🗑️  Dropped existing tables")
            
            # Create all tables
            db.create_all()
            click.echo("✅ Created new tables")
            
            # Show created tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            click.echo(f"📋 Tables: {', '.join(tables)}")
            
        except Exception as e:
            click.echo(f"❌ Error resetting database: {e}")
            return 1
    
    return 0


@cli.command()
@click.option('--env', default='development', help='Environment (development/production/testing)')
def show_stats(env):
    """Show database statistics"""
    click.echo(f"📊 Database statistics for {env} environment...")
    
    # Set environment
    os.environ['FLASK_ENV'] = env
    
    app = create_app()
    
    with app.app_context():
        try:
            # Count features
            feature_count = FeatureMap.query.count()
            click.echo(f"🔧 Features: {feature_count}")
            
            # Count labels
            label_count = FeatureLabel.query.count()
            click.echo(f"🏷️  Labels: {label_count}")
            
            # Count unique labels
            unique_labels = db.session.query(FeatureLabel.label).distinct().count()
            click.echo(f"🏷️  Unique labels: {unique_labels}")
            
            # Show source distribution
            community_count = FeatureMap.query.filter_by(ec_proprietary='COMMUNITY').count()
            ec_count = FeatureMap.query.filter_by(ec_proprietary='EC').count()
            unknown_count = feature_count - community_count - ec_count
            
            click.echo(f"📈 Source distribution:")
            click.echo(f"   Community: {community_count}")
            click.echo(f"   Edgecore: {ec_count}")
            click.echo(f"   Unknown: {unknown_count}")
            
        except Exception as e:
            click.echo(f"❌ Error getting statistics: {e}")
            return 1
    
    return 0


@cli.command()
@click.option('--env', default='development', help='Environment (development/production/testing)')
@click.option('--limit', default=10, help='Number of features to show')
def list_features(env, limit):
    """List features in database"""
    click.echo(f"📋 Listing {limit} features from {env} environment...")
    
    # Set environment
    os.environ['FLASK_ENV'] = env
    
    app = create_app()
    
    with app.app_context():
        try:
            features = FeatureMap.query.limit(limit).all()
            
            if not features:
                click.echo("No features found.")
                return
            
            for feature in features:
                labels = [label.label for label in feature.labels]
                click.echo(f"🔧 {feature.feature_key}")
                click.echo(f"   Description: {feature.feature_n1 or 'N/A'}")
                click.echo(f"   Category: {feature.category or 'N/A'}")
                click.echo(f"   Source: {feature.ec_proprietary or 'N/A'}")
                click.echo(f"   Labels: {', '.join(labels) if labels else 'None'}")
                click.echo()
            
        except Exception as e:
            click.echo(f"❌ Error listing features: {e}")
            return 1
    
    return 0


if __name__ == '__main__':
    cli()