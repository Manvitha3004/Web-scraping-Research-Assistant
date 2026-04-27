import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import './Canvas3D.css';

export function Canvas3D() {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xfaf8f3);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 8;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight * 0.4);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);

    // Create rotating geometries with pastel colors
    const pastelColors = [
      0xa8d8ea, // pastel cyan
      0xffd089b, // pastel amber
      0xd4a5d4, // pastel purple
      0xa8d5ba, // pastel green
      0xffc0e0, // pastel pink
    ];

    const group = new THREE.Group();
    scene.add(group);

    // Create multiple rotating cubes
    const cubes = [];
    for (let i = 0; i < 5; i++) {
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const material = new THREE.MeshPhongMaterial({
        color: pastelColors[i % pastelColors.length],
        emissive: pastelColors[i % pastelColors.length],
        emissiveIntensity: 0.3,
        wireframe: false,
      });
      const cube = new THREE.Mesh(geometry, material);

      const angle = (i / 5) * Math.PI * 2;
      cube.position.x = Math.cos(angle) * 4;
      cube.position.y = Math.sin(angle) * 4;
      cube.position.z = Math.sin(i * 0.5);

      group.add(cube);
      cubes.push({ mesh: cube, angle });
    }

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 0.8);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    const pointLight2 = new THREE.PointLight(0xa8d8ea, 0.5);
    pointLight2.position.set(-5, -5, 5);
    scene.add(pointLight2);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);

      // Rotate group
      group.rotation.x += 0.001;
      group.rotation.y += 0.002;

      // Individual cube rotation
      cubes.forEach((cube, index) => {
        cube.mesh.rotation.x += 0.01;
        cube.mesh.rotation.y += 0.015;
        cube.mesh.position.z += Math.sin(Date.now() * 0.001 + index) * 0.01;
      });

      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      const newWidth = window.innerWidth;
      const newHeight = window.innerHeight * 0.4;

      renderer.setSize(newWidth, newHeight);
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={containerRef} className="canvas-3d-container" />;
}
