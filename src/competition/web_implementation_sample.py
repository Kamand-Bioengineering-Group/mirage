"""
Sample Flask Application for XPECTO Competition System

This is a demonstrative implementation showing how the competition system
would be integrated into a Flask web application using Firebase as the backend.
"""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import uuid
from datetime import datetime

# Import competition components
from .core.models import Player, PlayerAttempt, Scenario, SimulationResults
from .data.storage import FirebaseStorageProvider
from .services.competition_service import CompetitionService
from .services.simulation_integration import SimulationIntegration

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

# Initialize Firebase (in production, use environment variables for credentials)
try:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully.")
except Exception as e:
    print(f"Warning: Firebase could not be initialized. Using stub for demo: {e}")
    db = None


# Initialize storage provider and competition service
storage_provider = FirebaseStorageProvider(firebase_app=firebase_admin)
competition_service = CompetitionService(storage_provider)

# Create a simulation engine factory (to be implemented based on deployment needs)
def create_engine():
    """Create and return a new epidemic engine instance."""
    try:
        from src.mirage.engines.base import EngineV1
        return EngineV1()
    except ImportError:
        print("Warning: Could not import epidemic engine. Using placeholder.")
        return None


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Player Management

@app.route('/api/players', methods=['POST'])
def register_player():
    """Register a new player."""
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    player = competition_service.register_player(
        name=data.get('name', ''),
        email=data.get('email', '')
    )
    
    return jsonify({
        'player_id': player.id,
        'name': player.name,
        'message': 'Player registered successfully'
    })

@app.route('/api/players/<player_id>', methods=['GET'])
def get_player(player_id):
    """Get player information."""
    player = competition_service.get_player(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    return jsonify({
        'id': player.id,
        'name': player.name,
        'email': player.email,
        'created_at': player.created_at.isoformat()
    })

@app.route('/api/players/<player_id>/strategy', methods=['POST'])
def update_strategy(player_id):
    """Update a player's strategy document."""
    data = request.json
    if not data or 'strategy' not in data:
        return jsonify({'error': 'Strategy document is required'}), 400
    
    success = competition_service.update_player_strategy(
        player_id=player_id,
        strategy_doc=data.get('strategy', '')
    )
    
    if not success:
        return jsonify({'error': 'Failed to update strategy'}), 400
    
    return jsonify({'message': 'Strategy updated successfully'})

# Scenarios

@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    """List available scenarios."""
    scenarios = competition_service.list_scenarios()
    
    return jsonify({
        'scenarios': [s.to_dict() for s in scenarios]
    })

@app.route('/api/scenarios/<scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    """Get scenario details."""
    scenario = competition_service.get_scenario(scenario_id)
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    
    return jsonify(scenario.to_dict())

# Simulation and Attempts

@app.route('/api/simulations', methods=['POST'])
def run_simulation():
    """Run a simulation and record the attempt."""
    data = request.json
    if not data or 'player_id' not in data or 'scenario_id' not in data:
        return jsonify({'error': 'Player ID and scenario ID are required'}), 400
    
    player_id = data.get('player_id')
    player_name = data.get('player_name', '')
    scenario_id = data.get('scenario_id')
    is_official = data.get('is_official', False)
    
    # Create engine and simulation integration
    engine = create_engine()
    if not engine:
        return jsonify({'error': 'Could not create simulation engine'}), 500
    
    simulation = SimulationIntegration(engine)
    
    # Get scenario configuration
    scenario = competition_service.get_scenario(scenario_id)
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    
    # Configure simulation
    try:
        simulation.configure_from_scenario(scenario)
    except Exception as e:
        return jsonify({'error': f'Failed to configure simulation: {str(e)}'}), 500
    
    # Run simulation (in production, this would be a background job)
    try:
        # Parse interventions (in production, would need secure execution model)
        interventions = []
        # TODO: implement secure intervention execution
        
        # Run simulation
        raw_results = simulation.run_simulation(
            steps=data.get('steps', 730),
            interventions=interventions
        )
        
        # Process results
        results = competition_service.process_simulation_results(
            player_id=player_id,
            scenario_id=scenario_id,
            simulation_data=raw_results
        )
        
        # Record attempt
        success, error = competition_service.record_attempt(
            player_id=player_id,
            player_name=player_name,
            scenario_id=scenario_id,
            results=results,
            is_official=is_official
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Simulation completed successfully',
            'results': results.to_dict()
        })
    except Exception as e:
        return jsonify({'error': f'Simulation failed: {str(e)}'}), 500

@app.route('/api/players/<player_id>/attempts', methods=['GET'])
def list_player_attempts(player_id):
    """List a player's attempts."""
    scenario_id = request.args.get('scenario_id')
    is_official = request.args.get('is_official')
    
    # Convert is_official to boolean if provided
    if is_official is not None:
        is_official = is_official.lower() == 'true'
    
    attempts = competition_service.get_player_attempts(
        player_id=player_id,
        scenario_id=scenario_id,
        is_official=is_official
    )
    
    return jsonify({
        'attempts': [a.to_dict() for a in attempts]
    })

# Leaderboard

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the current leaderboard."""
    entries = competition_service.get_leaderboard()
    
    return jsonify({
        'leaderboard': [e.to_dict() for e in entries]
    })

# Admin endpoints (would require authentication in production)

@app.route('/api/admin/scenarios', methods=['POST'])
def create_scenario():
    """Create a new scenario (admin only)."""
    # In production, would verify admin credentials
    data = request.json
    if not data:
        return jsonify({'error': 'Scenario data required'}), 400
    
    try:
        scenario = Scenario(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', 'New Scenario'),
            description=data.get('description', ''),
            seed=data.get('seed', f"seed_{uuid.uuid4()}"),
            r0=data.get('r0', 2.5),
            initial_infections=data.get('initial_infections', {'capital': 100}),
            initial_resources=data.get('initial_resources', 1000),
            difficulty=data.get('difficulty', 'standard'),
            parameters=data.get('parameters', {})
        )
        
        storage_provider.save_scenario(scenario)
        return jsonify({
            'message': 'Scenario created successfully',
            'scenario': scenario.to_dict()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to create scenario: {str(e)}'}), 500


if __name__ == '__main__':
    # For development only
    app.run(debug=True, host='0.0.0.0', port=5000) 