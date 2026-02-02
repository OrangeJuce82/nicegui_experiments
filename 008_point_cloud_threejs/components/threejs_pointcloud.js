// Three.js Point Cloud Component using Three.js directly

export default {
    template: "<div ref='container'></div>",
    props: {
        resource_path: String,
        positions: Array,
        colors: Array,
        pointSize: Number,
        fps: { type: Number, default: 60 },
        enableAnimation: { type: Boolean, default: true },
    },
    async mounted() {
        await this.$nextTick();

        // Load Three.js from CDN
        await this.loadScriptFromCDN("https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js");
        // Load Stats.js from CDN
        await this.loadScriptFromCDN("https://cdn.jsdelivr.net/npm/stats.js@0.17.0/build/stats.min.js");

        this.initScene();
    },
    methods: {
        initScene() {
            const container = this.$refs.container;
            const width = container.clientWidth || 800;
            const height = container.clientHeight || 600;

            // Create scene
            this.scene = new THREE.Scene();
            this.scene.background = new THREE.Color(0x111111);

            // Create camera
            this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
            this.camera.position.z = 8;

            // Create renderer
            this.renderer = new THREE.WebGLRenderer({ antialias: true });
            this.renderer.setSize(width, height);
            container.appendChild(this.renderer.domElement);

            // Add Stats
            this.stats = new Stats();
            this.stats.showPanel(0); // 0: fps, 1: ms, 2: mb
            this.stats.dom.style.position = 'absolute';
            this.stats.dom.style.top = '0px';
            this.stats.dom.style.left = '0px';
            container.appendChild(this.stats.dom);

            // Create point cloud geometry
            this.createPointCloud();

            // Setup animation with configurable FPS
            this.animationTime = 0;
            this.lastFrameTime = 0;
            this.frameInterval = 1000 / this.fps;

            // Add orbit controls manually (simple mouse interaction)
            this.setupMouseControls();

            // Start animation loop
            this.animate();

            // Handle resize
            window.addEventListener('resize', () => this.onWindowResize());
        },

        createPointCloud() {
            const positions = this.positions || [];
            const colors = this.colors || [];
            const pointSize = this.pointSize || 0.15;

            const geometry = new THREE.BufferGeometry();
            const positionArray = new Float32Array(positions.length * 3);
            const colorArray = new Float32Array(colors.length * 3);

            // Fill position array
            for (let i = 0; i < positions.length; i++) {
                positionArray[i * 3] = positions[i][0];
                positionArray[i * 3 + 1] = positions[i][1];
                positionArray[i * 3 + 2] = positions[i][2];
            }

            // Fill color array
            for (let i = 0; i < colors.length; i++) {
                colorArray[i * 3] = colors[i][0];
                colorArray[i * 3 + 1] = colors[i][1];
                colorArray[i * 3 + 2] = colors[i][2];
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positionArray, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));

            // Store reference for updates
            this.positionAttribute = geometry.getAttribute('position');

            // Create material with vertex colors
            const material = new THREE.PointsMaterial({
                size: pointSize,
                vertexColors: true,
                sizeAttenuation: true,
            });

            // Create point cloud
            this.pointCloud = new THREE.Points(geometry, material);
            this.scene.add(this.pointCloud);

            // Store geometry for updates
            this.geometry = geometry;
        },

        updatePositions(newPositions) {
            if (!this.positionAttribute) return;

            const positions = newPositions || this.positions || [];
            const positionArray = this.positionAttribute.array;

            for (let i = 0; i < positions.length; i++) {
                positionArray[i * 3] = positions[i][0];
                positionArray[i * 3 + 1] = positions[i][1];
                positionArray[i * 3 + 2] = positions[i][2];
            }

            this.positionAttribute.needsUpdate = true;
        },

        animatePoints() {
            if (!this.positionAttribute || !this.positions) return;

            const positionArray = this.positionAttribute.array;
            const numPoints = this.positions.length;

            // Calculate Z positions using the same formula as Python
            for (let i = 0; i < numPoints; i++) {
                const x = this.positions[i][0];
                const y = this.positions[i][1];
                const z = Math.sin(x * 1.0 + this.animationTime) * Math.cos(y * 1.0 + this.animationTime) + 1;
                positionArray[i * 3 + 2] = z;
            }

            this.positionAttribute.needsUpdate = true;
        },

        updateColors(newColors) {
            if (!this.geometry) return;

            const colors = newColors || this.colors || [];
            const colorArray = this.geometry.getAttribute('color').array;

            for (let i = 0; i < colors.length; i++) {
                colorArray[i * 3] = colors[i][0];
                colorArray[i * 3 + 1] = colors[i][1];
                colorArray[i * 3 + 2] = colors[i][2];
            }

            this.geometry.getAttribute('color').needsUpdate = true;
        },

        animate(timestamp) {
            requestAnimationFrame((t) => this.animate(t));

            if (!this.enableAnimation) return;

            const currentTime = timestamp || 0;
            const deltaTime = currentTime - this.lastFrameTime;

            // Throttle to FPS
            if (deltaTime < this.frameInterval) return;

            this.lastFrameTime = currentTime - (deltaTime % this.frameInterval);

            // Update stats
            this.stats.update();

            // Animate points if enabled
            if (this.enableAnimation) {
                this.animationTime += 0.05;
                this.animatePoints();
            }

            this.renderer.render(this.scene, this.camera);
        },

        setupMouseControls() {
            let isDragging = false;
            let previousMousePosition = { x: 0, y: 0 };

            const container = this.$refs.container;

            container.addEventListener('mousedown', (e) => {
                isDragging = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });

            container.addEventListener('mousemove', (e) => {
                if (!isDragging) return;

                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;

                // Rotate the point cloud
                this.pointCloud.rotation.y += deltaX * 0.01;
                this.pointCloud.rotation.x += deltaY * 0.01;

                previousMousePosition = { x: e.clientX, y: e.clientY };
            });

            container.addEventListener('mouseup', () => {
                isDragging = false;
            });

            container.addEventListener('mouseleave', () => {
                isDragging = false;
            });

            // Zoom with wheel
            container.addEventListener('wheel', (e) => {
                e.preventDefault();
                this.camera.position.z += e.deltaY * 0.01;
                this.camera.position.z = Math.max(2, Math.min(20, this.camera.position.z));
            });
        },

        onWindowResize() {
            const container = this.$refs.container;
            const width = container.clientWidth;
            const height = container.clientHeight;

            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        },

        loadScriptFromCDN(url) {
            return new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = url;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        },
    },
};
