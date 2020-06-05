function addBackground(svg, margin, height, width) {
    svg.append("rect")
        .attr("x", 0)
        .attr("y", margin.top + 1)
        .attr("width", width - margin.right)
        .attr("height", height - margin.bottom - margin.top - 1)
        .attr("fill", "rgb(248, 248, 248)");
}

(function average_month_temperatures() {

    let margin = ({top: 20, right: 0, bottom: 20, left: 0});
    let height = 100;
    let width = 500;

    const svg = d3.select('.average-month-temperatures__chart').append('svg')
        .attr('viewBox', [0, 0, width, height]);

    const dateFormat = d3.utcParse('%Y-%m-%d');

    let data = Object.assign(
        d3.json('/getAverageMonthTemperatures').then(data => {

            let yAxis = g => g
                .attr('transform', `translate(${margin.left},0)`)
                .attr('class', 'axis axis--y')
                .call(d3.axisRight(y)
                    .ticks(3)
                    .tickFormat(u => u + ' °C')
                    .tickSize(width - margin.left - margin.right))
                .call(g => g.select('.domain')
                    .remove())
                .call(g => g.selectAll('.tick line')
                    .attr('stroke-opacity', 0.25)
                    .attr('stroke-dasharray', '1,1'))
                .call(g => g.selectAll('.tick text')
                    .attr('x', 0)
                    .attr('dy', -3));

            let xAxis = g => g
                .attr('transform', `translate(0, ${height - margin.bottom})`)
                .attr('class', 'axis axis--x')
                .call(d3.axisBottom(x)
                    //.ticks(width / 60)
                    .ticks(d3.timeYear.every(10))
                    .tickFormat(d3.timeFormat('%Y'))
                    .tickSizeOuter(0))
                .call(g => g.select('.domain')
                    .remove())
                .call(g => g.selectAll('.tick line')
                    .attr('stroke-opacity', 0.25));

            let y = d3.scaleLinear()
                .domain([
                        Math.round((d3.min(data, d => d.value) - 1) / 5) * 5,
                        Math.round((d3.max(data, d => d.value) + 1) / 5) * 5,
                    ])
                .range([height - margin.bottom, margin.top]);

            let x = d3.scaleTime()
                .domain(d3.extent(data, d => dateFormat(d.date)))
                .range([margin.left, width - margin.right]);

            let line = d3.line()
                .defined(d => !isNaN(d.value))
                .x(d => x(dateFormat(d.date)))
                .y(d => y(d.value))
                /*.curve(d3.curveBasis)*/;

            addBackground(svg, margin, height, width);

            svg.append('g')
                .call(xAxis);

            svg.append('g')
                .call(yAxis);

            svg.append('path')
                .datum(data)
                .attr('class', 'line')
                .attr('fill', 'none')
                .attr('stroke', '#777777')
                .attr('stroke-width', 1.5)
                .attr('stroke-linejoin', 'round')
                .attr('stroke-linecap', 'round')
                .attr('d', line);

            let sortByValues = (data.sort(function(a, b) { return b.value - a.value }));

            // show 6 hottest julys
            svg.selectAll(null).data(data).enter()
                .filter(d => (d.value >= sortByValues[5].value))
                    .append('circle')
                    .attr('class', 'circle circle--max')
                    .attr('r', 3)
                    .attr('cx', d => x(dateFormat(d.date)))
                    .attr('cy', d => y(d.value));

            // show 6 coldest julys
            svg.selectAll(null).data(data).enter()
                .filter(d => (d.value <= sortByValues[sortByValues.length - 6].value))
                    .append('circle')
                    .attr('class', 'circle circle--min')
                    .attr('r', 3)
                    .attr('cx', d => x(dateFormat(d.date)))
                    .attr('cy', d => y(d.value));

        })
        .catch((error) => {
            throw error;
        }));

}());


(function average_temperatures() {

    let margin = ({top: 0, right: 0, bottom: 20, left: 0});
    let height = 100;
    let width = 500;

    const svg = d3.select(".average-temperatures__chart").append('svg')
        .attr("viewBox", [0, 0, width, height]);

    const dateFormat = d3.utcParse("%Y");

    let data = Object.assign(
        d3.json('/getAverageTemperatures').then(data => {

            let yAxis = g => g
                .attr("transform", `translate(${margin.left},0)`)
                .attr("class", "axis axis--y")
                .call(d3.axisRight(y)
                    .ticks(3)
                    .tickFormat(u => u + ' °C')
                    .tickSize(width - margin.left - margin.right))
                .call(g => g.select('.domain')
                    .remove())
                .call(g => g.selectAll('.tick line')
                    .attr("stroke-opacity", 0.25)
                    .attr("stroke-dasharray", "1,1"))
                .call(g => g.selectAll('.tick text')
                    .attr("x", 0)
                    .attr("dy", -3));

            let xAxis = g => g
                .attr("transform", `translate(0, ${height - margin.bottom})`)
                .attr("class", "axis axis--x")
                .call(d3.axisBottom(x)
                    //.ticks(width / 60)
                    .ticks(d3.timeYear.every(10))
                    .tickFormat(d3.timeFormat('%Y'))
                    .tickSizeOuter(0))
                .call(g => g.select('.domain')
                    .remove())
                .call(g => g.selectAll('.tick line')
                    .attr("stroke-opacity", 0.25));

            let y = d3.scaleLinear()
                .domain([
                        (d3.min(data, d => d.value) - 1),
                        (d3.max(data, d => d.value) + 1),
                    ])
                .range([height - margin.bottom, margin.top]);

            let x = d3.scaleTime()
                .domain(d3.extent(data, d => dateFormat(d.year)))
                .range([margin.left, width - margin.right]);

            let line = d3.line()
                .defined(d => !isNaN(d.value))
                .x(d => x(dateFormat(d.year)))
                .y(d => y(d.value))
                /*.curve(d3.curveBasis)*/;

            let linearRegression = d3.regressionLinear()
                .x(d => (dateFormat(d.year)))
                .y(d => (d.value));

            let res = linearRegression(data)

            addBackground(svg, margin, height, width);

            svg.append("g")
              .call(xAxis);

            svg.append("g")
              .call(yAxis);

            svg.append("path")
              .datum(data)
              .attr("fill", "none")
              .attr("stroke", "#777777")
              .attr("stroke-width", 1.5)
              .attr("stroke-linejoin", "round")
              .attr("stroke-linecap", "round")
              .attr("d", line);


            let res_line = d3.line()
                  .x((d) => x(d[0]))
                  .y((d) => y(d[1]));

                svg.append("path")
                  .datum(res)
                  .attr("d", res_line)
                  .attr("fill", "none")
                  .attr("stroke", "#f54a2b")
                  .attr("stroke-width", 1)
                  .attr("stroke-linejoin", "round")
                  .attr("stroke-linecap", "round")


        })
        .catch((error) => {
            throw error;
        }));
}());



(function temperatures_per_month_and_year() {

    let width = 500;

    const dateFormat = d3.utcParse("%Y-%m-%d");
    const months = [
        'Januar',
        'Februar',
        'März',
        'April',
        'Mai',
        'Juni',
        'Juli',
        'August',
        'September',
        'Oktober',
        'November',
        'Dezember',
    ]

    let data = Object.assign(
        d3.json('/getTemperaturesPerMonthAndYear').then(data => {

            data = d3.nest()
                .key(d => d.month)
                .entries(data);

            data.forEach(function(node, i) {

                let height = 44;
                let margin = ({top: 8, right: 60, bottom: 8, left: 0});

                switch(i) {
                    case 0:
                        height = 55;
                        margin.top = 20;
                        break;
                    case data.length - 1:
                        height = 55;
                        margin.bottom = 20;
                        break;
                }

                let yAxis = g => g
                    .attr("transform", `translate(${margin.left},0)`)
                    .attr("class", "axis axis--y axis--small")
                    .call(d3.axisRight(y)
                        .ticks(3)
                        .tickFormat(u => u + ' °C')
                        .tickSize(width - margin.left - margin.right))
                    .call(g => g.select('.domain')
                        .remove())
                    .call(g => g.selectAll('.tick line')
                        .attr("stroke-opacity", 0.25)
                        .attr("stroke-dasharray", "1,1"))
                    .call(g => g.selectAll('.tick text')
                        .attr("x", 0)
                        .attr("dy", -3));

                let xAxisTop = g => g
                    .attr("transform", `translate(0, ${margin.top})`)
                    .attr("class", "axis axis--x")
                    .call(d3.axisTop(x)
                        .ticks(d3.timeYear.every(10))
                        .tickFormat(d3.timeFormat('%Y'))
                        .tickSizeOuter(0))
                    .call(g => g.select('.domain')
                        .remove())
                    .call(g => g.selectAll('.tick line')
                        .attr("stroke-opacity", 0.25));

                let xAxisBottom = g => g
                    .attr("transform", `translate(0, ${height - margin.bottom})`)
                    .attr("class", "axis axis--x")
                    .call(d3.axisBottom(x)
                        .ticks(d3.timeYear.every(10))
                        .tickFormat(d3.timeFormat('%Y'))
                        .tickSizeOuter(0))
                    .call(g => g.select('.domain')
                        .remove())
                    .call(g => g.selectAll('.tick line')
                        .attr("stroke-opacity", 0.25));

                let y = d3.scaleLinear()
                    /*.domain([
                        (d3.min(node.values, d => d.value) - 1),
                        (d3.max(node.values, d => d.value) + 1),
                    ])*/
                    .domain([-10, 20])
                    .range([height - margin.bottom, margin.top]);

                let x = d3.scaleTime()
                    .domain(d3.extent(node.values, d => {
                        return dateFormat(d.date);
                    }))
                    .range([margin.left, width - margin.right]);

                let line = d3.line()
                    //.defined(d => !isNaN(d.values[i].value))
                    .x(d => {
                        return x(dateFormat(d.date))
                    })
                    .y(d => {
                        return y(d.value);
                    })
                    /*.curve(d3.curveBasis)*/;

                let svg = d3.select(".temperatures_per_month_and_year__chart")
                    .append('svg')
                    .attr("viewBox", [0, 0, width, height]);

                addBackground(svg, margin, height, width);

                switch(i) {
                    case 0:
                        svg.append("g")
                            .call(xAxisTop);
                        break;
                    case data.length - 1:
                        svg.append("g")
                            .call(xAxisBottom);
                        break;
                }

                svg.append("g")
                    .call(yAxis);

                svg.append("path")
                    .datum(() => {
                        return node.values;
                    })
                    .attr("fill", "none")
                    .attr("stroke", "#777777")
                    .attr("stroke-width", 1)
                    .attr("stroke-linejoin", "round")
                    .attr("stroke-linecap", "round")
                    .attr("d", line);


                let sortByValues = (node.values.sort(function(a, b) { return b.value - a.value }));

                // show hottest month
                svg.selectAll(null).data(() =>  node.values).enter()
                    .filter(d => (d.value >= sortByValues[0].value))
                        .append('circle')
                        .attr('class', 'circle circle--max')
                        .attr('r', 3)
                        .attr('cx', d => x(dateFormat(d.date)))
                        .attr('cy', d => y(d.value));

                // show coldest month
                svg.selectAll(null).data(() =>  node.values).enter()
                    .filter(d => (d.value <= sortByValues[sortByValues.length - 1].value))
                        .append('circle')
                        .attr('class', 'circle circle--min')
                        .attr('r', 3)
                        .attr('cx', d => x(dateFormat(d.date)))
                        .attr('cy', d => y(d.value));


                svg.append('text')
                    .attr('x', width - margin.right + 5)
                    .attr('y', i === 0 ? 28 : 16)
                    .attr('class', 'months')
                    //.attr("dy", ".71em")
                    .text(months[i]);

            })
        })
        .catch((error) => {
            throw error;
        }));
}());






(function getWeatherStation() {
    d3.json('/getWeatherStations')
        .then((data) => {

            /*d3.select("body")
                .selectAll("p")
                .data(data)
                .enter()
                .append("p")
                .text(function(d) {
                    return d.name + ", ";
            });*/


            // add the options to the dropdown
            d3.select(".js-weatherstation-selector__select")
              .selectAll('myOptions')
                .data(data)
              .enter()
                .append('option')
              .text(function (d) { return d.name; })
              .attr("value", function (d) { return d.id; });


        // A function that update the chart
        function update(selectedGroup) {
          // Create new data with the selection?
          let dataFilter = data.map(function(d){return {time: d.time, value:d[selectedGroup]} })

          // Give these new data to update line
          line
              .datum(dataFilter)
              .transition()
              .duration(1000)
              .attr("d", d3.line()
                .x(function(d) { return x(+d.time) })
                .y(function(d) { return y(+d.value) })
              )
              .attr("stroke", function(d){ return myColor(selectedGroup) })
        }

        // When the dropdown is changed, run the updateChart function
        d3.select('.js-weatherstation-selector__select').on('change', function(d) {
            // recover the option that has been chosen
            let selectedOption = d3.select(this).property('value');
            // run the updateChart function with this selected option
            update(selectedOption);
        })

    });
}());









(function temperatures() {
    function parseTime(offset) {
        let date = new Date(2017, 0, 1); // chose an arbitrary day
        return d3.timeMinute.offset(date, offset);
    }

    function row(d) {
        return {
            activity: d.year,
            time: parseTime(d.date),
            value: +d.measured_value
        };
    }


    let margin = { top: 30, right: 10, bottom: 30, left: 60 },
        width = 800 - margin.left - margin.right,
        height = 1400 - margin.top - margin.bottom;

    // Percent two area charts can overlap
    let overlap = 0.6;

    let formatTime = d3.timeFormat('%b');

    let chart = d3.select('.temperatures-evolution__chart').append('svg')
            //.attr('width', width + margin.left + margin.right)
            //.attr('height', height + margin.top + margin.bottom)
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr("viewBox", "0 0 1540 1000")
            .append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    let x = function(d) { return d.month; },
        xScale = d3.scaleTime().range([0, width]),
        xValue = function(d) { return xScale(x(d)); },
        xAxis = d3.axisBottom(xScale).tickFormat(formatTime);

    let y = function(d) { return Math.pow(d.measured_value, 1); },
        yScale = d3.scaleLinear(),
        yValue = function(d) { return yScale(y(d)); };

    let activity = function(d) { return d.key; },
        activityScale = d3.scaleBand().range([0, height]),
        activityValue = function(d) { return activityScale(activity(d)); },
        activityAxis = d3.axisLeft(activityScale);

    let area = d3.area()
        .x(xValue)
        .y1(yValue);

    let line = area.lineY1();


    d3.json('/getTemperatures')
        .then((dataFlat) => {

            // Sort by time
            /*dataFlat.sort(function (a, b) {
                return a.year - b.year;
            });*/

            let data = d3.nest()
                .key(function (d) {
                    return d.year;
                })
                .entries(dataFlat);

            // Sort activities by peak activity time
            /*function peakTime(d) {
                let i = d3.scan(d.values, function (a, b) {
                    return y(b) - y(a);
                });
                return d.values[i].year;
            }

            data.sort(function (a, b) {
                return peakTime(b) - peakTime(a);
            });*/

            xScale.domain(d3.extent(dataFlat, x));

            activityScale.domain(data.map(function (d) {
                return d.key;
            }));

            let areaChartHeight = (1 + overlap) * (height / activityScale.domain().length);

            yScale
                .domain(d3.extent(dataFlat, y))
                .range([areaChartHeight, 0]);

            //area.y0(yScale(0));

            chart.append('g').attr('class', 'axis axis--x')
                .attr('transform', 'translate(0,' + height + ')')
                .call(xAxis);

            chart.append('g').attr('class', 'axis axis--activity')
                .call(activityAxis);

            let gActivity = chart.append('g').attr('class', 'activities')
                .selectAll('.activity').data(data)
                .enter().append('g')
                .attr('class', function (d) {
                    return 'activity activity--' + d.key;
                })
                .attr('transform', function (d) {
                    let ty = activityValue(d) - activityScale.bandwidth() + 5;
                    //return 'translate(0,' + ty + ')';
                    return 'translate(' + (width - ty) + ',' + ty + ')';
                });

            /*gActivity.append('path').attr('class', 'area')
                .datum(function (d) {
                    return d.values;
                })
                .attr('d', area);*/

            gActivity.append('path').attr('class', 'line')
                .datum(function (d) {
                    return d.values;
                })
                .attr('d', line);

        })
        .catch((error) => {
            throw error;
        });

}());
