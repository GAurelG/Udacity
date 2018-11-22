# Improving journey planning using the 2008 flight arrival delay data

The following document is related to [this Tableau Dashboard]("arrival delay dashboard").
## Summary

The main finding is that all airline and airport are not equally sensitive to delay. As someone travelling regularly, I found out that an important cause of stress during a travel is the ability to catch a connecting transportation medium in case the previous part of the trip is delayed. One way of avoiding this stress in most of the cases is to plan sufficient time to switch transport even wheen you are a bit delayed. The data from the 2008 Reporting on-Time performance of the Unated States of America Bureau of Transportation Statistics gives us the possibility of creating a dashboard helping anyone plan a travel and decide the reasonable delay they want to account for, when preparing their travel.

## Design

This Dashboard was thought as a place to iteratively look for the interresting delay data. The top selection dropdown for Destination City, helps access the interresting data faster. The map is placed at the top left in order to be the second element to be interacted with (for a left-right/up-down reading person). The map was decided as the second interaction point, as some people are more visual oriented and it could act as a visual selection part. Another use case for this selection map, is that it allows to make a regional selection of airport and compare the different airports directly on the map. To allow comparison of airports on the map, a color scale for delay was implemented on the map with geen for "less delay than other selected airports" to yellow and the red for "more delay than other selected airports".

The next item is the airline delay graph on the top right side.It represent the arrival delay data aggregated on the airline level for the selected reagion... These dealy data are representing the mean delay in yellow, and the 90th persentile of delay in red. The mean was chosen as it reflects what reasonable expectation of dely could be. The 90th percentile of delay was included as it gives information on extreme delay. It also gives indication on how the average can be skewed because of extreme values. This graph was though as a mean to compare the reliability of different airlines. The color coding was used to visually separate the different level of aggregation and help the reader understand what would be a "bad" case scenario and what would be a more normal expectation. Red was chosen to outline "bad case scenario" as it is often used to represent bad results. The yellow for the average was chosen as it is less charged than green but still gives a nice contrast to the eyes.

Below the airline graph, I  placed the different time level (day of week and month) aggregation. These graphs are placed there, to guide the user in using the airline graph as a selector first, and then have the repartition of delay over time. This graphics was decided to be a bar graph as the different days or month level are thought as indepent values. It may not be totally the case in reality, but this way we are not implying any linear relationship between different days or month. Bar graphs with their use of area and height as comparative means, helps the reader see the difference and compare data points faster. I went with an average delay value representation in these graphs because the estimation is that the user wants an estimation of "standard" delay and adding any extra aggregation would bloat the visual representaion and won't add more insight. Also the average being sensitive to extreme event helps capturing the possible difference in delay distribution within an airline. For those graphics, the yellow color from the airline average delay graphic on top was kept to have a consistent color coding of information (yellow = average delay).

One of the main Design choice was to allow each representation to be the starting filter fo all other graphs. While the path of recursively refining the selection is encourage in a specific way by the layout chosen (for reader using a left to right and up to down scheme). It was really important to me to give the reader the possibility to explore the data in other ways than I thought. 
Several changes where made to the graphics to came up to that design. I made the choice to explain the changes within the feedback part as I like to have the context of each change nearby.

Overall I think that the feedback helped me get a more focused and expressive dashboard. the first draft had lacking part that I was aware of (mainly the legend and coloring part. But the change of focus to a destination based dashboard, and the inclusion of a time representation was a extreme improvement to the amount of information presented and to the overal quality of the design.

## Feedack

**Version one**:
it started out as a small combination of map and a bargraph to look at delay per airline. (see "dashboard V1")
**Feedback V1**:
While presenting that dashboard to my girlfriend, I directly got the feedback that it would be usefull to get an analysis per destination airport. The main argument was that not all airport suffer the same passenger loads and might not suffer the same delay. Another really interresting Idea was to include a time dimension to the analysis.

**Version two**:
After that feedback I went back to the graphical representation and used the "destination City" as a general filter. I then improved the representation of delay through time by looking at average delay per days of the week and per month. After adding these graphics to the mix I found that the dashboard was cramped. I didn't noticed at first as I worked on a computer with a small screen. To address that, I changed the dashboard layout to give it a better size and allow it to fit better in the screens. I also decided to give the dashboard user a better way of managing the delay they want to account for. To that effect I changed the graph showing the delay per airline to also show the third quartile delay value. That way, One can decide how much risks they want to take into account when planning their trip. (Dashboard V2)

**Feedback V2**:
The feedback was more positive this time. the main critics concerned the legend in the day of week and month graphs to be abstract and not really helpfull. Another critics was the different titles and legend that weren't well explanatory. Another idea was to maybe look at the hourly variation of delay.

**Version three**:
I had a good thought and tried to make an hourly representation of delay. I decided not to include it in the dashboard as I find that when planning a travel there are usually other constraint than just possible delay that influence the choice of time for a flight or a train. I think that the hourly breakup of delay would only clutter the visuals and hide the important information. I changed the different legend and added some more speacking axis title as well as a general title. (Dashboard V3 = final version)

## Resources

- [2008 USA flight data](http://stat-computing.org/dataexpo/2009/the-data.html "flight data")
- [OpenFlight Airport and airline data](https://openflights.org/data.html "airline and airport information")
- [Tableau forums](https://community.tableau.com/community/forums "Tableau community")


