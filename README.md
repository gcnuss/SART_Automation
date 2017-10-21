# Seattle Adventure Run Trounament (SART) Automation

### Description
The goal of this project is to automate Cascade Orienteering Club's SART bracket / heat set up and results calculations to support more efficient processing during the tournament.  This tournament is currently hosted as an 80 person tournament with an initial seeding race and 5 tournament rounds.  All participants get to participate in all rounds, meaning heat assignments need to be made for all of them in each round.
In previous years, I have run the time keeping software and used MS Excel to supplement with all of the number crunching required to process heat assignments and results real time during the event.

### Current Results
The 2017 tournament was successfully run using orienteering time keeping software SportsSoftware and bracket creation, heat assignments, and results processing executed utilizing a Python class I created and ran in the included Jupyter Notebook.  This approach improved fidelity and efficiency relative to the previous years using Excel.

## Future Improvements
For next year's tournament, I want to add functionality to the Python class to automatically address breaking of ties and people who do not start / participate in a given round.  These two aspects were partially manual this year.  I included means to check for ties and DNS's but the program simply gives a warning message and then I addressed them manually.  In particular breaking ties will require pulling in additional data from the time keeping system relative to what I used this year (raw overall time results).  The additional data required is the splits data, since breaking ties requires checking placement at the prior checkpoint.
