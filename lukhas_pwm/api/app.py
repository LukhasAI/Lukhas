from fastapi import FastAPI
from lukhas_pwm.api.audit import router as audit_router
from lukhas_pwm.api.feedback import router as feedback_router
from lukhas_pwm.api.tools import router as tools_router

app = FastAPI(title="LUKHΛS PWM API ⚛️🧠🛡️")
app.include_router(audit_router)
app.include_router(feedback_router)
app.include_router(tools_router)
