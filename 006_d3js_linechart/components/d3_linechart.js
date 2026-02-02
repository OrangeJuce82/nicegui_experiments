// Load D3.js from CDN
const loadD3 = async () => {
    if (typeof d3 === 'undefined') {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://d3js.org/d3.v7.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
};

function emitEvent(eventName, detail) {
    const event = new CustomEvent(eventName, { detail });
    window.dispatchEvent(event);
}

export default {
    template: '<div class="d3-linechart-container"></div>',
    props: {
        resource_path: String,
        data: Array,
        width: Number,
        height: Number,
    },
    data() {
        return {
            chartWidth: 0,
            chartHeight: 400,
        };
    },
    async mounted() {
        await this.$nextTick();
        
        // Load D3.js
        await loadD3();
        
        this.chartWidth = this.width || this.$el.clientWidth;
        this.chartHeight = this.height || 400;
        
        this.drawChart();
        window.addEventListener('resize', this.handleResize);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize);
    },
    watch: {
        data: {
            handler(newData) {
                this.drawChart();
            },
            deep: true,
        },
    },
    methods: {
        handleResize() {
            this.chartWidth = this.$el.clientWidth;
            this.drawChart();
        },
        drawChart() {
            if (!this.data || this.data.length === 0) return;
            
            const container = this.$el;
            const margin = { top: 20, right: 30, bottom: 30, left: 50 };
            const width = this.chartWidth - margin.left - margin.right;
            const height = this.chartHeight - margin.top - margin.bottom;
            
            // Clear previous chart
            d3.select(container).selectAll('svg').remove();
            
            const svg = d3.select(container)
                .append('svg')
                .attr('width', this.chartWidth)
                .attr('height', this.chartHeight)
                .append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Parse dates
            const parseDate = d3.timeParse('%Y-%m-%d');
            const parsedData = this.data.map(d => ({
                date: parseDate(d.date),
                value: d.value,
            }));
            
            // Scales
            const x = d3.scaleTime()
                .domain(d3.extent(parsedData, d => d.date))
                .range([0, width]);
            
            const y = d3.scaleLinear()
                .domain([0, d3.max(parsedData, d => d.value) * 1.1])
                .range([height, 0]);
            
            // Grid lines
            svg.append('g')
                .attr('class', 'grid')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x)
                    .tickSize(-height)
                    .tickFormat('')
                );
            
            svg.append('g')
                .attr('class', 'grid')
                .call(d3.axisLeft(y)
                    .tickSize(-width)
                    .tickFormat('')
                );
            
            // Axes
            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x));
            
            svg.append('g')
                .attr('class', 'axis')
                .call(d3.axisLeft(y));
            
            // Line
            const line = d3.line()
                .x(d => x(d.date))
                .y(d => y(d.value))
                .curve(d3.curveMonotoneX);
            
            // Add line path
            svg.append('path')
                .datum(parsedData)
                .attr('class', 'line')
                .attr('d', line);
            
            // Add dots
            const tooltip = d3.select(container)
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0);
            
            svg.selectAll('.dot')
                .data(parsedData)
                .enter()
                .append('circle')
                .attr('class', 'dot')
                .attr('cx', d => x(d.date))
                .attr('cy', d => y(d.value))
                .attr('r', 5)
                .attr('fill', '#4fc3f7')
                .style('cursor', 'pointer')
                .on('mouseover', function(event, d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('r', 8)
                        .attr('fill', '#ff7043');
                    
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', 1);
                    tooltip.html(`Date: ${d.date.toLocaleDateString()}<br>Value: ${d.value}`)
                        .style('left', (event.offsetX + 10) + 'px')
                        .style('top', (event.offsetY - 10) + 'px');
                })
                .on('mouseout', function() {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('r', 5)
                        .attr('fill', '#4fc3f7');
                    
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                });
        },
    },
};
