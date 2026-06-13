"""
HLD Case: Automated Vehicle Damage Auto-Penalty Pipeline
Difficulty: Hard
Category: Real-World Cases

Problem:
Design an Automated Vehicle Damage Auto-Penalty Pipeline.
The system is triggered when a rental car is returned. High-resolution images of the vehicle 
are uploaded from the return kiosk. The system must:
1. Detect any new physical damages (scratches, dents, cracks) comparing against historical images.
2. If damage is detected, run a valuation lookup to estimate repair cost.
3. Automatically charge the user's card on file.
4. Notify the user with a detailed damage report and receipt.

Key Non-Functional Requirements:
- Images must be processed reliably within 5 minutes of return.
- Charging logic must be strictly idempotent (no duplicate charges under any retry scenario).
- System must scale to handle 50,000 car returns per day globally.

Instructions:
Review the system requirements and write down your component architecture design, API endpoints, 
and database tables. Click "Compare Design" to check against the production-grade architecture.
"""

# --- SYSTEM INTERFACE SIGNATURES (For structural understanding) ---
class DamageDetectionPipeline:
    """
    Design overview of endpoints and main worker workflows.
    """
    def upload_return_telemetry(self, reservation_id: str, images: list[bytes]) -> dict:
        """
        API Endpoint: Triggered when vehicle is returned.
        Should upload images, store them, and enqueue an asynchronous processing job.
        """
        return {"status": "enqueued", "job_id": "job_12345"}

    def process_damage_detection(self, job_id: str):
        """
        Background Worker: Runs Computer Vision model, compares against historical snapshots,
        and saves findings to Database.
        """
        pass

    def execute_penalty_billing(self, reservation_id: str, damage_details: dict) -> bool:
        """
        Billing Worker: Idempotently charges user card and fires success notification.
        """
        pass
