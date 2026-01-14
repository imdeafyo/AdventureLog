// Resolves a CSS color (including CSS variables and modern color functions like oklch)
// to a concrete `rgb(r, g, b)` string at runtime.
//
// This is useful for MapLibre style layers, which may not reliably parse modern
// color syntaxes across all environments.
export function resolveThemeColor(cssVarName: string, fallback: string): string {
	if (typeof window === 'undefined' || typeof document === 'undefined') return fallback;

	const raw = getComputedStyle(document.documentElement).getPropertyValue(cssVarName).trim();
	if (!raw) return fallback;

	// Try to resolve via the browser’s computed styles so we always end up with rgb(...)
	const el = document.createElement('span');
	el.style.position = 'absolute';
	el.style.left = '-99999px';
	el.style.top = '-99999px';

	// DaisyUI v5 theme vars are typically like: `--color-primary: oklch(...);`
	// If we ever get a raw OKLCH triplet, wrap it.
	const candidate = raw.includes('(') ? raw : `oklch(${raw})`;
	el.style.color = candidate;

	document.body.appendChild(el);
	const computed = getComputedStyle(el).color;
	el.remove();

	return computed && computed !== 'rgba(0, 0, 0, 0)' ? computed : fallback;
}

export function withAlpha(color: string, alpha: number): string {
	const a = Math.max(0, Math.min(1, alpha));
	const rgbMatch = color.match(/^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/i);
	if (rgbMatch) {
		const r = Number(rgbMatch[1]);
		const g = Number(rgbMatch[2]);
		const b = Number(rgbMatch[3]);
		return `rgba(${r}, ${g}, ${b}, ${a})`;
	}

	const rgbaMatch = color.match(
		/^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([0-9.]+)\s*\)$/i
	);
	if (rgbaMatch) {
		const r = Number(rgbaMatch[1]);
		const g = Number(rgbaMatch[2]);
		const b = Number(rgbaMatch[3]);
		return `rgba(${r}, ${g}, ${b}, ${a})`;
	}

	// Fallback: return original color if we can't safely parse.
	return color;
}
