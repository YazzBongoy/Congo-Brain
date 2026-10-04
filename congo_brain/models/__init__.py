"""SQLAlchemy ORM models for Congo-Brain.

Every model must be imported here: alembic/env.py does `import congo_brain.models`
to register `Base.metadata`, so a model that is not re-exported from this package
is invisible to `--autogenerate` and never reaches the migration history. The
GEOS entities were missed this way until revision c3f9a1d47b2e.
"""

from congo_brain.models.audit import AuditEvent  # noqa: F401
from congo_brain.models.budget import Budget, Transaction  # noqa: F401
from congo_brain.models.citizen import FAQ, CitizenRight, Contact, Procedure  # noqa: F401
from congo_brain.models.geos.entities import Budget as GeosBudget  # noqa: F401
from congo_brain.models.geos.entities import Citizen as GeosCitizen  # noqa: F401
from congo_brain.models.geos.entities import Company as GeosCompany  # noqa: F401
from congo_brain.models.geos.entities import Contract as GeosContract  # noqa: F401
from congo_brain.models.geos.entities import Indicator as GeosIndicator  # noqa: F401
from congo_brain.models.geos.entities import Infrastructure as GeosInfrastructure  # noqa: F401
from congo_brain.models.geos.entities import Market as GeosMarket  # noqa: F401
from congo_brain.models.geos.entities import Ministry as GeosMinistry  # noqa: F401
from congo_brain.models.geos.entities import Payment as GeosPayment  # noqa: F401
from congo_brain.models.geos.entities import Project as GeosProject  # noqa: F401
from congo_brain.models.geos.entities import Province as GeosProvince  # noqa: F401
from congo_brain.models.geos.entities import PublicService as GeosPublicService  # noqa: F401
from congo_brain.models.geos.entities import Resource as GeosResource  # noqa: F401
from congo_brain.models.geos.entities import Tax as GeosTax  # noqa: F401
from congo_brain.models.investment import Investment  # noqa: F401
from congo_brain.models.security_alert import SecurityAlert  # noqa: F401
from congo_brain.models.transparency import TransparencyReport  # noqa: F401
from congo_brain.models.user import User  # noqa: F401
