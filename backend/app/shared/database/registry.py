# Niveau 0 — pas de FK vers d'autres modèles custom
import app.modules.users.models          # noqa: F401
import app.modules.partners.models       # noqa: F401
import app.modules.settings.models

# Niveau 0bis — dépendance circulaire avec users (User.center_id/branch_id ↔
# CenterLicense.activated_by → users.id). Sans impact car les FK sont résolues
# par nom de table sur Base.metadata, pas par ordre d'import de classes.
import app.modules.centers.models        # noqa: F401

# Niveau 1 — dépend de partners
import app.modules.promo_codes.models    # noqa: F401

# Niveau 2 — pas de dépendances custom
import app.modules.exams.models          # noqa: F401
import app.modules.plans.models          # noqa: F401  ← monter ici

# Niveau 3 — dépend de exams
import app.modules.questions.models      # noqa: F401

# Niveau 4 — dépend de users + exams + promo_codes + plans
import app.modules.payments.models       # noqa: F401  ← après plans
import app.modules.ai_credit_purchases.models  # noqa
import app.modules.exam_access.models    # noqa: F401

# Niveau 5 — dépend de users + exams + questions (+ payments pour referrals)
import app.modules.exam_sessions.models  # noqa: F401
import app.modules.corrections.models  # noqa: F401
import app.modules.schreiben_simulator.models  # noqa: F401
import app.modules.sprechen_agent.models  # noqa: F401
import app.modules.referrals.models      # noqa: F401  ← dépend de users + payments