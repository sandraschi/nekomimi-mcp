import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

interface Props {
	token: string;
	intensity: number;
}

const BONE_POSES: Record<string, Record<string, [number, number, number]>> = {
	attending: {
		head: [0, 0, 0],
		neck: [0, 0, 0],
		spine: [0, 0, 0],
		earLeft: [15, 0, 0],
		earRight: [15, 0, 0],
	},
	nod: {
		head: [15, 0, 0],
		neck: [5, 0, 0],
		earLeft: [10, 0, 0],
		earRight: [10, 0, 0],
	},
	shake: {
		head: [0, 0, 25],
		neck: [0, 0, 10],
		earLeft: [5, -5, 0],
		earRight: [5, 5, 0],
	},
	sulk: {
		head: [20, 0, -15],
		neck: [10, 0, -5],
		spine: [-10, 0, 0],
		earLeft: [-20, 10, 0],
		earRight: [-20, -10, 0],
	},
	bashful: {
		head: [10, -15, 15],
		neck: [5, -5, 5],
		earLeft: [-15, 20, 0],
		earRight: [-15, -20, 0],
	},
	amused: {
		head: [-5, 0, 0],
		spine: [5, 0, 0],
		earLeft: [20, 5, 0],
		earRight: [20, -5, 0],
	},
	playful: {
		head: [-10, 0, 20],
		spine: [10, 15, 0],
		earLeft: [25, 15, 0],
		earRight: [10, -10, 0],
	},
	confused: {
		head: [0, -20, 15],
		neck: [0, -10, 5],
		earLeft: [5, 20, 0],
		earRight: [20, -5, 0],
	},
	retreat: {
		head: [25, 0, 0],
		spine: [-20, 0, 0],
		earLeft: [-25, 15, 0],
		earRight: [-25, -15, 0],
	},
	surprise: {
		head: [-20, 0, 0],
		neck: [-10, 0, 0],
		spine: [15, 0, 0],
		earLeft: [30, 0, 0],
		earRight: [30, 0, 0],
	},
	bow: {
		head: [30, 0, 0],
		neck: [20, 0, 0],
		spine: [45, 0, 0],
		earLeft: [0, 0, 0],
		earRight: [0, 0, 0],
	},
	happy: {
		head: [-10, 0, 0],
		spine: [5, 0, 0],
		earLeft: [30, 10, 0],
		earRight: [30, -10, 0],
	},
	sad: {
		head: [25, -5, 0],
		neck: [15, 0, 0],
		spine: [-10, 0, 0],
		earLeft: [-10, 5, 0],
		earRight: [-10, -5, 0],
	},
	angry: {
		head: [-5, 0, 0],
		neck: [-5, 0, 0],
		spine: [10, 0, 0],
		earLeft: [-30, -10, 0],
		earRight: [-30, 10, 0],
	},
	nekomimi: {
		head: [-5, -15, 15],
		neck: [5, -5, 10],
		spine: [5, 5, 0],
		earLeft: [30, -10, 0],
		earRight: [20, 10, 0],
	},
};

export default function VRMViewer({ token, intensity }: Props) {
	const canvasRef = useRef<HTMLCanvasElement>(null);
	const groupRef = useRef<THREE.Group | null>(null);
	const [poseCount, setPoseCount] = useState(0);

	useEffect(() => {
		if (!canvasRef.current) return;
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0x18181b);
		const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
		camera.position.set(0, 0.8, 2.5);
		camera.lookAt(0, 0.5, 0);
		const renderer = new THREE.WebGLRenderer({
			canvas: canvasRef.current,
			antialias: true,
		});
		renderer.setSize(280, 320);
		renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
		const amb = new THREE.AmbientLight(0xffffff, 0.6);
		scene.add(amb);
		const dir = new THREE.DirectionalLight(0xffffff, 1.0);
		dir.position.set(2, 4, 3);
		scene.add(dir);
		const group = new THREE.Group();
		groupRef.current = group;
		scene.add(group);
		const mat = new THREE.MeshStandardMaterial({
			color: 0xf59e0b,
			roughness: 0.6,
		});
		const makeSphere = (
			x: number,
			y: number,
			z: number,
			r: number,
			bone?: string,
		) => {
			const m = new THREE.Mesh(new THREE.SphereGeometry(r, 12, 12), mat);
			m.position.set(x, y, z);
			if (bone) m.userData.bone = bone;
			group.add(m);
			return m;
		};
		const makeCyl = (
			x: number,
			y: number,
			z: number,
			h: number,
			r: number,
			color = 0xf59e0b,
			bone?: string,
		) => {
			const m = new THREE.Mesh(
				new THREE.CylinderGeometry(r, r, h, 8),
				new THREE.MeshStandardMaterial({ color, roughness: 0.6 }),
			);
			m.position.set(x, y, z);
			if (bone) m.userData.bone = bone;
			group.add(m);
			return m;
		};
		makeCyl(0, 0.6, 0, 0.7, 0.25, 0x27272a, "spine");
		makeSphere(0, 1.15, 0, 0.15, "head");
		makeCyl(0, 0.95, 0, 0.08, 0.06, 0x3f3f46, "neck");
		makeCyl(-0.35, 0.85, 0, 0.4, 0.04, 0x52525b);
		makeCyl(0.35, 0.85, 0, 0.4, 0.04, 0x52525b);
		const earMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b });
		const earGeo = new THREE.ConeGeometry(0.06, 0.1, 4);
		const earL = new THREE.Mesh(earGeo, earMat);
		earL.position.set(-0.1, 1.28, 0);
		earL.userData.bone = "earLeft";
		earL.userData.neutralRot = new THREE.Euler(-0.2, 0, -0.3);
		earL.rotation.copy(earL.userData.neutralRot);
		group.add(earL);
		const earR = new THREE.Mesh(earGeo, earMat);
		earR.position.set(0.1, 1.28, 0);
		earR.userData.bone = "earRight";
		earR.userData.neutralRot = new THREE.Euler(-0.2, 0, 0.3);
		earR.rotation.copy(earR.userData.neutralRot);
		group.add(earR);
		let angle = 0;
		const animate = () => {
			requestAnimationFrame(animate);
			angle += 0.01;
			group.position.y = Math.sin(angle) * 0.01;
			renderer.render(scene, camera);
		};
		animate();
		return () => {
			renderer.dispose();
			scene.clear();
		};
	}, []);

	useEffect(() => {
		const bones = BONE_POSES[token] || BONE_POSES.attending;
		let count = 0;
		for (const [bone, rot] of Object.entries(bones)) {
			count++;
			if (!groupRef.current) continue;
			const child = groupRef.current.children.find(
				(c: THREE.Object3D) => c.userData.bone === bone,
			);
			if (!child) continue;
			const neutral = child.userData.neutralRot;
			const scale = intensity || 1;
			if (neutral) {
				child.rotation.set(
					neutral.x + (rot[0] * Math.PI * scale) / 180,
					neutral.y + (rot[1] * Math.PI * scale) / 180,
					neutral.z + (rot[2] * Math.PI * scale) / 180,
				);
			} else {
				child.rotation.set(
					(rot[0] * Math.PI * scale) / 180,
					(rot[1] * Math.PI * scale) / 180,
					(rot[2] * Math.PI * scale) / 180,
				);
			}
		}
		setPoseCount(count);
	}, [token, intensity]);

	return (
		<div className="flex flex-col items-center">
			<canvas
				ref={canvasRef}
				className="rounded-lg"
				style={{ width: 280, height: 320 }}
			/>
			<div className="text-xs text-zinc-500 mt-1">
				{poseCount} bones + ears | {token}
			</div>
		</div>
	);
}
