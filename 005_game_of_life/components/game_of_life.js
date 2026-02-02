

export default {
    template: "<div></div>",
    props: {
        resource_path: String,
        speed: Number,
        playing: Boolean,
        drawing: String,
        hex_color: String,
    },
    async mounted() {
        await this.$nextTick(); // NOTE: wait for window.path_prefix to be set
        await this.loadScriptFromCDN("https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js");

        this.generation_num = 0;
        this.grid = [];
        this.size = 16;
        this.cols = 0;
        this.rows = 0;
        this.padding = [0, 0];

        this.sketch = new p5((sketch) => {
            sketch.setup = function () {
                sketch.createCanvas(sketch.windowWidth, sketch.windowHeight);
            };
            sketch.draw = this.draw;
            sketch.mouseDragged = this.modify_drawing;
            sketch.mouseClicked = this.modify_drawing;
        }, this.$el);

        // Add event listeners
        window.onresize = this.resize;
        window.onload = this.init_grid_with_default_pattern;
    },
    methods: {
        get_available_size() {
            const headers = document.getElementsByClassName("q-header")
            const header_height = headers.length === 1 ? headers[0].offsetHeight : 0;

            const footers = document.getElementsByClassName("q-footer")
            const footer_height = footers.length === 1 ? footers[0].offsetHeight : 0;

            return {
                width: this.sketch.windowWidth,
                height: this.sketch.windowHeight - header_height - footer_height,
            };
        },
        generate_next_grid_then_draw() {
            this.generate_next_grid();
            this.draw();
        },
        draw() {
            // FPS is normally 60, but we increase generation depends on speed factor
            const increase_gen = this.sketch.frameCount % Math.floor(10 / this.speed) === 0;
            if (!this.sketch.mouseIsPressed && !increase_gen) {
                return;
            }

            if (this.playing && increase_gen) {
                this.generate_next_grid();
            }

            const alive_color = this.sketch.color(this.hex_color)
            this.sketch.clear();
            for (let i = 0; i < this.cols; i++) {
                for (let j = 0; j < this.rows; j++) {
                    if (this.grid[i][j] === 0) {
                        this.sketch.fill(255);
                    } else {
                        this.sketch.fill(alive_color);
                    }
                    this.sketch.square(
                        i * this.size + this.padding[0],
                        j * this.size + this.padding[1],
                        this.size
                    );
                }
            }
        },
        modify_drawing() {
            const col = Math.floor((this.sketch.mouseX - this.padding[0]) / this.size);
            const row = Math.floor((this.sketch.mouseY - this.padding[1]) / this.size);

            // Check value exists then update
            if ((this.grid[col] || [])[row] !== undefined) {
                this.grid[col][row] = (this.drawing === "pencil") ? 1 : 0;
            }
        },
        count_neighbors(x, y) {
            let sum = 0;
            for (let i = -1; i < 2; i++) {
                for (let j = -1; j < 2; j++) {
                    let nx = (x + i + this.cols) % this.cols;
                    let ny = (y + j + this.rows) % this.rows;
                    sum += this.grid[nx][ny];
                }
            }
            sum -= this.grid[x][y];
            return sum;
        },
        generate_next_grid() {
            let next_grid = [];
            for (let i = 0; i < this.cols; i++) {
                next_grid[i] = [];
                for (let j = 0; j < this.rows; j++) {
                    const neighbors = this.count_neighbors(i, j);
                    const is_alive = this.grid[i][j] === 1;

                    if (is_alive && neighbors < 2) {
                        next_grid[i][j] = 0;
                    } else if (is_alive && (neighbors === 2 || neighbors === 3)) {
                        next_grid[i][j] = 1;
                    } else if (is_alive && neighbors > 3) {
                        next_grid[i][j] = 0;
                    } else if (!is_alive && neighbors === 3) {
                        next_grid[i][j] = 1;
                    } else {
                        next_grid[i][j] = this.grid[i][j];
                    }
                }
            }
            this.grid = next_grid;
            this.generation_num += 1;
            emitEvent("gol__generation_num", this.generation_num);
        },
        init_grid(mode = "0") {
            const available_size = this.get_available_size()
            this.sketch.resizeCanvas(available_size.width, available_size.height);

            this.generation_num = 0;
            emitEvent("gol__generation_num", this.generation_num);

            // Add padding when computing number of cols and rows
            this.cols = Math.floor(available_size.width / this.size) - 2;
            this.rows = Math.floor(available_size.height / this.size) - 2;
            this.padding = [
                (available_size.width - this.cols * this.size) / 2,
                (available_size.height - this.rows * this.size) / 2,
            ]

            // Init array
            const grid = [];
            for (let i = 0; i < this.cols; i++) {
                grid[i] = [];
                for (let j = 0; j < this.rows; j++) {
                    if (mode === "random") {
                        grid[i][j] = Math.floor(this.sketch.random(2))
                    } else if (mode === "resize" && (this.grid[i] || [])[j] !== undefined) {
                        grid[i][j] = this.grid[i][j];
                    } else {
                        grid[i][j] = 0;
                    }
                }
            }
            this.grid = grid;
        },
        init_grid_with_default_pattern() {
            this.init_grid();

            if (this.cols < 2 || this.rows < 2) {
                return;
            }

            // Default pattern
            this.grid[1][0] = 1;
            this.grid[2][1] = 1;
            this.grid[0][2] = 1;
            this.grid[1][2] = 1;
            this.grid[2][2] = 1;
        },
        resize() {
            this.init_grid("resize");
        },
        loadScriptFromCDN(url) {
            return new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = url;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
    },
};
