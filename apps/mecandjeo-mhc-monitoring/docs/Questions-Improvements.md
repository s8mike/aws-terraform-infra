* For clarity, when test are ran, include the purpose for the test. This should be explanatory enough for other users.

* Since I am using gitbash as a complimentary terminal, you can also include the terminal commands alongside powershell in your documentation.
* Secure password should include upper case letter, special letters like !, @, #, %, $, etc in addition to numbers and lowercase letters.
* User email should be in the form: john-Doe@example.com
* We should push every phase to the upstream on completion instead of waiting to complete all the phases before pushing to github.
* Each file should have an intro inline comment of what it does. Current inline comment for each block should be sustained.
* In models.py, under Class-Shift:
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True), ended_at ...., nullable=True should not be empty. The shift should end
    This should be applicable to other class in the models.py

* In the "Shift" can we have an option where an operator will select his particular shift i.e Shift A, B or C?

* Add the phase that a code is introduced or added to a file.

# Newly added after Phase 4 implementation

# Standard work categories from the project intent document.
NATURE_OF_WORK_VALUES = [
    "across_heights_portside",
    "deck_free_bay",
    "underdeck_free_bay",
    "underdeck_across_heights",
    "loading_export_3_4",
    "loading_empty_single",
    "loading_empty_twin",
    "discharge_oog",
    "tight_space_cranes",
]

* loading_export_3_4 => This include Loading export either on underdeck-free_bay or underdeck across_heights. This should distinguished and seperated as an improvement to avoid ambuiguity.
 loading_export_3_4 (meaning free bay and across heights)
 3==Loading export on Free bay
 4==Loading export across heights

# Delays types should be assigned keys
For example:
Awaiting Containers = ACon
Awaiting Trucks = AT
Awaiting Stevedores=AStev,
Awaiting Clerks=AClerks,
etc
This we should review before final approval.

# Running Local test in tests/
While it is observed that the tests/ contains all tests executed by you, I will appreciate if you can give me sample, with guide to also execute on my system. This is to enable me have an insight (do it yourself approach). This is when i believe everything has been integrated (fastAPI ==> Database)


# Repeat Testing for each phase
Would sincerely appreciate if each phase is tested one after the other as documented in tests/ again when prompted after we might completed the whole codes and phases, using the individual test commands. I will also appreciate the purpose of each test and why it is necessary as an inline comment.

# Appliation Structure
Current "Application Structure" in Roadmap.md needs to be updated to align with current files.

# After Phase 10, what next?
After we have completed phase 10, what other phases are we looking at? Frontend UI and UX (using react or best frontend tool of choice), Frontend cicd integration (github and github actions), etc. I am particularly interested in improving my knowledge and skills in devops tools like kubernetes, helm, argocd, argocd-gitops, etc. I will appreciate if you have structured phases that can help with this, with emphasis on improving the applications using these tools; add, commit, push and seeing application deployed.

# Intention after frontend ui/ux phase
The intention is to make a presentation of this app to user or a potential subscriber, showcasing the functionality of the application.

# Request after phase 8
Maybe i should have a documention for each phases probably in a PHASE-DOCS/ in docs/
The documentation for each phase should give a work through of what the phase is all about (purpose, objectives,etc), the various local test commands, files changed or modified during that phase. It should be more like an explicit guide to new users. Once this can be done, we proceed with phase 9 (we can use the shared resources or opt for a standalone infrasture)