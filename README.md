# Google ADK BigQuery Demo

1. `google auth login --update-adc`
1. Update `demo_app/terraform/locals.tf` and `demo_app/event_agent/.env` with GCP project name
1. Run terraform from `demo_app/terraform`
1. Run `sh ./sql.sh`
1. Install requirements in frontend and run `streamlit run demo_app/frontend/main.py`
1. Run `adk web demo_app`

## License
Written by Issac Goldstand <issacg@cloudex.co.il>

Copyright 2025 Cloudex Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
