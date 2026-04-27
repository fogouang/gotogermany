# Niveau 0 — pas de FK vers d'autres modèles custom
import app.modules.users.models          # noqa: F401
import app.modules.partners.models       # noqa: F401

# Niveau 1 — dépend de partners
import app.modules.promo_codes.models    # noqa: F401

# Niveau 2 — pas de dépendances custom
import app.modules.exams.models          # noqa: F401
import app.modules.plans.models          # noqa: F401  ← monter ici

# Niveau 3 — dépend de exams
import app.modules.questions.models      # noqa: F401

# Niveau 4 — dépend de users + exams + promo_codes + plans
import app.modules.payments.models       # noqa: F401  ← après plans
import app.modules.exam_access.models    # noqa: F401

# Niveau 5 — dépend de users + exams + questions
import app.modules.exam_sessions.models  # noqa: F401