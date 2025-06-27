"""
SQLAlchemy-based routes for feature management
"""
from flask import request, render_template
from sqlalchemy import and_, or_
from models.base import db
from models import FeatureMap, FeatureLabel


def feature_list_sqlalchemy(app_config):
    """Feature list route using SQLAlchemy ORM"""
    # Get filter parameters
    label_filter = request.args.get('label', '')
    branch_filter = request.args.get('branch', '')
    support_filter = request.args.get('support', '')
    source_filter = request.args.get('source', '')  # community or edgecore
    
    try:
        # Start with base query
        query = FeatureMap.query
        
        # Apply label filter
        if label_filter:
            query = query.join(FeatureLabel).filter(FeatureLabel.label == label_filter)
        
        # Apply source filter
        if source_filter:
            if source_filter == 'community':
                query = query.filter(FeatureMap.ec_proprietary.ilike('COMMUNITY'))
            elif source_filter == 'edgecore':
                query = query.filter(FeatureMap.ec_proprietary.ilike('EC'))
        
        # Apply branch filter (specific branch must have 'Support' status)
        if branch_filter:
            branch_column = getattr(FeatureMap, branch_filter, None)
            if branch_column:
                query = query.filter(branch_column == 'Support')
        
        # Apply support status filter (any branch has this status)
        if support_filter:
            branch_conditions = [
                FeatureMap.ec_sonic_2111 == support_filter,
                FeatureMap.ec_sonic_2211 == support_filter,
                FeatureMap.ec_sonic_2311_x == support_filter,
                FeatureMap.ec_sonic_2311_n == support_filter,
                FeatureMap.vs_202311 == support_filter,
                FeatureMap.ec_proprietary == support_filter
            ]
            query = query.filter(or_(*branch_conditions))
        
        # Execute query and get features
        features = query.order_by(FeatureMap.feature_key).all()
        
        # Get all labels for filter dropdown
        all_labels = db.session.query(FeatureLabel.label).distinct().order_by(FeatureLabel.label).all()
        all_labels = [label[0] for label in all_labels]
        
        # Convert features to format expected by template
        features_data = []
        for feature in features:
            feature_dict = {
                'feature_key': feature.feature_key,
                'feature_description': feature.feature_n1,
                'labels': [label.label for label in feature.labels],
                'branches': {
                    'ec_sonic_2111': feature.ec_sonic_2111,
                    'ec_sonic_2211': feature.ec_sonic_2211,
                    'ec_sonic_2311_x': feature.ec_sonic_2311_x,
                    'ec_sonic_2311_n': feature.ec_sonic_2311_n,
                    'vs_202311': feature.vs_202311,
                    'ec_proprietary': feature.ec_proprietary
                }
            }
            features_data.append(feature_dict)
        
        return render_template('feature_list.html', 
                             features=features_data,
                             all_labels=all_labels,
                             current_filters={
                                 'label': label_filter,
                                 'branch': branch_filter,
                                 'support': support_filter,
                                 'source': source_filter
                             },
                             config=app_config)
                             
    except Exception as e:
        return render_template('feature_list.html', 
                             features=[],
                             all_labels=[],
                             current_filters={},
                             error=str(e),
                             config=app_config)