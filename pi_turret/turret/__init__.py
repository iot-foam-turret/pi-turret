try:
    from pi_turret.turret.turret import Turret
except ImportError:
    from pi_turret.turret.mock_turret import Turret
