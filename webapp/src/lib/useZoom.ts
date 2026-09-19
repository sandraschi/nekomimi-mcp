import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "nekomimi-ui-zoom";
const MIN_ZOOM = 0.75;
const MAX_ZOOM = 1.5;
const STEP = 0.1;

function clamp(v: number): number {
	return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Math.round(v * 100) / 100));
}

function loadZoom(): number {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) return clamp(Number.parseFloat(raw));
	} catch {
		/* no storage */
	}
	return 1;
}

/** Ctrl+scroll UI zoom, persisted. Mandatory for native (Tauri) builds. */
export function useZoom(): {
	zoom: number;
	zoomIn: () => void;
	zoomOut: () => void;
	zoomReset: () => void;
	bindZoomKeys: (el: HTMLElement | null) => void;
} {
	const [zoom, setZoom] = useState<number>(loadZoom);

	useEffect(() => {
		try {
			localStorage.setItem(STORAGE_KEY, String(zoom));
		} catch {
			/* no storage */
		}
	}, [zoom]);

	const zoomIn = useCallback(() => setZoom((z) => clamp(z + STEP)), []);
	const zoomOut = useCallback(() => setZoom((z) => clamp(z - STEP)), []);
	const zoomReset = useCallback(() => setZoom(1), []);

	// Ctrl+0 resets zoom anywhere in the app.
	useEffect(() => {
		const onKey = (e: KeyboardEvent) => {
			if (e.ctrlKey && e.key === "0") {
				e.preventDefault();
				setZoom(1);
			}
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, []);

	const bindZoomKeys = useCallback((el: HTMLElement | null) => {
		if (!el) return;
		const onWheel = (e: WheelEvent) => {
			if (!e.ctrlKey) return;
			e.preventDefault();
			setZoom((z) => clamp(z + (e.deltaY < 0 ? STEP : -STEP)));
		};
		el.addEventListener("wheel", onWheel, { passive: false });
	}, []);

	return { zoom, zoomIn, zoomOut, zoomReset, bindZoomKeys };
}
