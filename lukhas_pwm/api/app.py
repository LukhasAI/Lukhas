from fastapi import FastAPI
from lukhas_pwm.api.audit import router as audit_router
from lukhas_pwm.api.feedback import router as feedback_router
from lukhas_pwm.api.tools import router as tools_router
from lukhas_pwm.api.incidents import router as incidents_router
from lukhas_pwm.api.metrics import router as metrics_router

app = FastAPI(title="LUKHΛS PWM API ⚛️🧠🛡️")
app.include_router(audit_router)
app.include_router(feedback_router)
app.include_router(tools_router)
app.include_router(incidents_router)
app.include_router(metrics_router)
