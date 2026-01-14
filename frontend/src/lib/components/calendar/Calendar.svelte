<script lang="ts">
	// @ts-ignore
	import Calendar from '@event-calendar/core';
	// @ts-ignore
	import TimeGrid from '@event-calendar/time-grid';
	// @ts-ignore
	import DayGrid from '@event-calendar/day-grid';
	// @ts-ignore
	import Interaction from '@event-calendar/interaction';
	import { t } from 'svelte-i18n';
	import { onMount } from 'svelte';

	export let events: Array<{
		id: string;
		start: string;
		end: string;
		title: string;
		backgroundColor?: string;
		extendedProps?: any;
	}> = [];

	export let onEventClick: ((event: any) => void) | null = null;
	export let height: string = 'auto';
	export let view: string = 'dayGridMonth';
	export let dayMaxEvents: number = 3;
	export let initialDate: string | Date | null = null;

	let plugins = [TimeGrid, DayGrid, Interaction];

	$: options = {
		view,
		events,
		date: initialDate || undefined,
		headerToolbar: {
			start: 'prev,next today',
			center: 'title',
			end: 'dayGridMonth,timeGridWeek,timeGridDay'
		},
		buttonText: {
			today: $t('calendar.today'),
			dayGridMonth: $t('calendar.month'),
			timeGridWeek: $t('calendar.week'),
			timeGridDay: $t('calendar.day')
		},
		height,
		eventDisplay: 'block',
		dayMaxEvents,
		moreLinkText: (num: number) => `+${num} more`,
		eventClick: (info: any) => {
			if (onEventClick) {
				onEventClick(info.event);
			}
		},
		eventMouseEnter: (info: any) => {
			info.el.style.cursor = 'pointer';
		},
		themeSystem: 'standard'
	};

	onMount(() => {
		// Add custom CSS for calendar styling
		const style = document.createElement('style');
		style.textContent = `
			.ec-toolbar {
				background: hsl(var(--b2)) !important;
				border-radius: 0.75rem !important;
				padding: 1.25rem !important;
				margin-bottom: 1.5rem !important;
				border: 1px solid hsl(var(--b3)) !important;
				box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
			}
			.ec-button {
				background: hsl(var(--b3)) !important;
				border: 1px solid hsl(var(--b3)) !important;
				color: hsl(var(--bc)) !important;
				border-radius: 0.5rem !important;
				padding: 0.5rem 1rem !important;
				font-weight: 500 !important;
				transition: all 0.2s ease !important;
			}
			.ec-button:hover {
				background: hsl(var(--b1)) !important;
				transform: translateY(-1px) !important;
				box-shadow: 0 4px 12px rgb(0 0 0 / 0.15) !important;
			}
			.ec-button.ec-button-active {
				background: hsl(var(--p)) !important;
				color: hsl(var(--pc)) !important;
				box-shadow: 0 4px 12px hsl(var(--p) / 0.3) !important;
			}
			.ec-day {
				background: hsl(var(--b1)) !important;
				border: 1px solid hsl(var(--b3)) !important;
				transition: background-color 0.2s ease !important;
			}
			.ec-day:hover {
				background: hsl(var(--b2)) !important;
			}
			.ec-day-today {
				background: hsl(var(--b2)) !important;
				position: relative !important;
			}
			.ec-day-today::before {
				content: '' !important;
				position: absolute !important;
				top: 0 !important;
				left: 0 !important;
				right: 0 !important;
				height: 3px !important;
				background: hsl(var(--p)) !important;
				border-radius: 0.25rem !important;
			}
			.ec-event {
				border-radius: 0.375rem !important;
				padding: 0.25rem 0.5rem !important;
				font-size: 0.75rem !important;
				font-weight: 600 !important;
				transition: all 0.2s ease !important;
				box-shadow: 0 1px 3px rgb(0 0 0 / 0.1) !important;
			}
			.ec-event:hover {
				transform: translateY(-1px) !important;
				box-shadow: 0 4px 12px rgb(0 0 0 / 0.15) !important;
			}
			.ec-view {
				background: hsl(var(--b1)) !important;
				border-radius: 0.75rem !important;
				overflow: hidden !important;
			}
		`;
		document.head.appendChild(style);
	});
</script>

<div class="card bg-base-100 shadow-2xl border border-base-300/50">
	<div class="card-body p-0">
		<Calendar {plugins} {options} />
	</div>
</div>
