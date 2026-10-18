<template>
    <v-container id="main">
        <div class="sketchfab-embed-wrapper"> <iframe title="Wooden Greenhouse with Plants" frameborder="0"
                allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true"
                allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport
                execution-while-not-rendered web-share
                src="https://sketchfab.com/models/5d4dbd36b7194730852ae59a8088e70b/embed"> </iframe>
            <p style="font-size: 13px; font-weight: normal; margin: 5px; color: #4A4A4A;"> <a
                    href="https://sketchfab.com/3d-models/wooden-greenhouse-with-plants-5d4dbd36b7194730852ae59a8088e70b?utm_medium=embed&utm_campaign=share-popup&utm_content=5d4dbd36b7194730852ae59a8088e70b"
                    target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> Wooden Greenhouse with
                    Plants </a> by <a
                    href="https://sketchfab.com/Nicholas01?utm_medium=embed&utm_campaign=share-popup&utm_content=5d4dbd36b7194730852ae59a8088e70b"
                    target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> Nicholas-3D </a> on <a
                    href="https://sketchfab.com?utm_medium=embed&utm_campaign=share-popup&utm_content=5d4dbd36b7194730852ae59a8088e70b"
                    target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;">Sketchfab</a></p>
        </div>
    </v-container>
</template>

<script setup>
import * as THREE from 'three';
import { onMounted } from 'vue';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// onMounted(() => {

//     const scene = new THREE.Scene();
//     const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
//     camera.position.z = 5;

//     const renderer = new THREE.WebGLRenderer();
//     renderer.setSize(window.innerWidth, window.innerHeight);
//     document.getElementById('main').appendChild(renderer.domElement);

//     const controls = new OrbitControls(camera, renderer.domElement);

//     const geometry = new THREE.BoxGeometry(1, 1, 1);
//     const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
//     const cube = new THREE.Mesh(geometry, material);
//     scene.add(cube);

//     function animate() {
//         requestAnimationFrame(animate);
//         controls.update();
//         // cube.rotation.x += 0.01;
//         // cube.rotation.y += 0.01;
//         renderer.render(scene, camera);
//     }
//     animate();
// })
</script>