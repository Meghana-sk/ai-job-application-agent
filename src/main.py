from __future__ import annotations
import json,os
from datetime import datetime,timezone
from src.applications.prepare import prepare_application
from src.reporting.summary import write_metrics
from src.scoring.matcher import evaluate
from src.search.discovery import dedupe_jobs
from src.search.providers import discover
from src.tracking.store import ApplicationStore

def _provider_config()->dict[str,list[str]]:
    raw=os.getenv("JOB_PROVIDER_BOARDS",'{"greenhouse":[],"lever":[]}')
    parsed=json.loads(raw)
    return {"greenhouse":parsed.get("greenhouse",[]),"lever":parsed.get("lever",[])}

def load_config(profile:dict)->dict:
    comp=profile.get("compensation",{})
    profile_min=int(float(comp.get("minimum_total_compensation_lpa",0) or 0)*100000)
    secret_min=int(os.getenv("MIN_COMPENSATION_INR","0"))
    return {"enabled":os.getenv("JOB_SEARCH_ENABLED","true").lower()=="true",
            "max_results":int(os.getenv("JOB_SEARCH_MAX_RESULTS","10")),
            "minimum_compensation_inr":profile_min or secret_min or 5000000}

def run()->None:
    run_started_at=datetime.now(timezone.utc)
    store=ApplicationStore()
    try:
        profile=store.get_candidate_profile()
        config=load_config(profile)
        if not config["enabled"]:
            write_metrics({"jobs_found":0,"matching_jobs":0,"applications_prepared":0,"applications_submitted":0,"errors":0}); return
        jobs=dedupe_jobs(discover(_provider_config()))
        matching=[]
        for job in jobs:
            evaluation=evaluate(job,config["minimum_compensation_inr"],profile)
            application_id=f"{job.provider}:{job.provider_job_id}"
            inserted=store.add_application({
                "application_id":application_id,"job_id":job.provider_job_id,"company":job.company,"role":job.title,
                "location":job.location,"work_mode":job.work_mode,"application_url":job.apply_url,"source":job.provider,
                "discovered_at":run_started_at.isoformat(),"role_match":evaluation["role_match"],
                "matched_skills":evaluation["matched_skills"],"missing_skills":evaluation["missing_skills"],
                "match_score":evaluation["score"],"compensation_value_inr":evaluation["compensation_value_inr"],
                "compensation_currency":"INR","compensation_disclosed":evaluation["compensation_disclosed"],
                "status":"discovered","first_seen_at":run_started_at.isoformat(),"last_updated_at":run_started_at.isoformat(),
                "notes":"; ".join(evaluation.get("review_reasons",[])),
            })
            if not inserted: continue
            store.record_status(application_id,"discovered")
            if evaluation["eligible"]:
                store.record_status(application_id,"matched"); matching.append((job,evaluation))
        prepared=0
        for job,evaluation in sorted(matching,key=lambda item:item[1]["score"],reverse=True)[:config["max_results"]]:
            prepare_application(job,evaluation,profile=profile)
            store.record_status(f"{job.provider}:{job.provider_job_id}","prepared")
            store.record_status(f"{job.provider}:{job.provider_job_id}","awaiting_approval")
            prepared+=1
        metrics=store.metrics_since(run_started_at.isoformat())
        metrics.update({"jobs_found":len(jobs),"matching_jobs":len(matching),"applications_prepared":prepared,"applications_submitted":0})
        write_metrics(metrics)
        print(f"Jobs found: {metrics['jobs_found']}")
        print(f"Matching jobs: {metrics['matching_jobs']}")
        print(f"Applications prepared: {metrics['applications_prepared']}")
        print("Applications submitted: 0 (approval required)")
        print(f"Errors: {metrics['errors']}")
    except Exception:
        write_metrics({"jobs_found":0,"matching_jobs":0,"applications_prepared":0,"applications_submitted":0,"errors":1}); raise
    finally: store.close()

if __name__=="__main__": run()
