<script lang="ts">
	import { t } from 'svelte-i18n';
	import CloseIcon from '~icons/mdi/close';
	import MapMarkerIcon from '~icons/mdi/map-marker';
	import ClockIcon from '~icons/mdi/clock';
	import { marked } from 'marked';

	export let show: boolean = false;
	export let event: any = null;
	export let isLoadingDetails: boolean = false;
	export let detailsError: string = '';
	export let location: string = '';
	export let description: string = '';
	export let onClose: () => void;
	export let timezoneMode: 'event' | 'local' = 'event';
	export let userTimezone: string = '';

	const renderMarkdown = (markdown: string) => {
		return marked(markdown);
	};
</script>

{#if show && event}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div class="modal modal-open">
		<div
			class="modal-box max-w-3xl p-0 bg-base-100 border border-base-300 shadow-2xl max-h-[90vh] flex flex-col"
		>
			<div
				class="relative bg-gradient-to-r from-primary via-primary/80 to-secondary/80 text-primary-content p-6"
			>
				<div
					class="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_top,_var(--p),_transparent_45%)]"
				></div>
				<div class="relative flex items-start justify-between gap-4">
					<div class="flex items-start gap-4">
						<div
							class="h-14 w-14 rounded-2xl bg-base-100/20 backdrop-blur flex items-center justify-center text-3xl shadow-inner"
						>
							{event.extendedProps?.icon || '📅'}
						</div>
						<div class="space-y-1">
							<p class="text-xs uppercase tracking-wide font-semibold opacity-80">
								{event.extendedProps?.type || 'Event'}
							</p>
							<h3 class="text-2xl font-bold leading-tight">
								{event.extendedProps?.adventureName || event.title}
							</h3>
							{#if event.extendedProps?.category}
								<div class="badge badge-primary badge-lg bg-base-100/20 text-base-100 mt-2">
									{event.extendedProps.category}
								</div>
							{/if}
						</div>
					</div>
					<button class="btn btn-ghost btn-sm btn-circle" on:click={onClose}>
						<CloseIcon class="w-5 h-5" />
					</button>
				</div>
			</div>

			<div class="p-6 space-y-5 overflow-y-auto">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="card bg-base-200/60 border border-base-300/70 shadow-sm">
						<div class="card-body p-4 space-y-2">
							<div class="flex items-center gap-3">
								<ClockIcon class="w-6 h-6 text-primary flex-shrink-0" />
								<div class="space-y-1">
									<div class="font-semibold text-base">
										{#if event.extendedProps?.isAllDay}
											{$t('calendar.all_day_event')}
										{:else if event.extendedProps?.formattedStart}
											{event.extendedProps.formattedStart}
											{#if event.extendedProps.formattedEnd !== event.extendedProps.formattedStart}
												→ {event.extendedProps.formattedEnd}
											{/if}
										{:else}
											{event.start}
										{/if}
									</div>
									<div class="text-xs text-base-content/70">
										{event.extendedProps?.timezoneLabel ||
											(timezoneMode === 'local'
												? `${$t('calendar.your timezone')} (${userTimezone})`
												: `${$t('calendar.event timezone')} (${event.extendedProps?.timezone || userTimezone})`)}
									</div>
								</div>
							</div>
						</div>
					</div>

					{#if location}
						<div class="card bg-base-200/60 border border-base-300/70 shadow-sm">
							<div class="card-body p-4">
								<div class="flex items-start gap-3">
									<MapMarkerIcon class="w-6 h-6 text-primary flex-shrink-0" />
									<div class="space-y-1">
										<div class="font-semibold text-base">{location}</div>
										{#if event.extendedProps?.route}
											<div class="text-sm text-base-content/70">{event.extendedProps.route}</div>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>

				{#if description}
					<div class="card bg-base-200/60 border border-base-300/70 shadow-sm">
						<div class="card-body p-4 space-y-3">
							<div class="flex items-center justify-between">
								<div class="font-semibold text-base">{$t('adventures.description')}</div>
							</div>
							<article class="prose max-w-none">
								{@html renderMarkdown(description || '')}
							</article>
						</div>
					</div>
				{:else if isLoadingDetails}
					<div class="flex items-center gap-2 text-sm text-base-content/70">
						<span class="loading loading-spinner loading-sm"></span>
						<span>{$t('immich.loading') + '...'}</span>
					</div>
				{:else if detailsError}
					<div class="alert alert-error text-sm">
						{detailsError}
					</div>
				{/if}

				<div class="flex flex-wrap items-center justify-between gap-3">
					{#if event.extendedProps?.adventureId}
						<a
							href={`/locations/${event.extendedProps.adventureId}`}
							class="btn btn-neutral btn-sm"
						>
							{$t('map.view_details')}
						</a>
					{/if}
					<div class="space-x-2">
						<button class="btn btn-primary btn-sm" on:click={onClose}>
							{$t('about.close')}
						</button>
					</div>
				</div>
			</div>
		</div>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-backdrop" on:click={onClose}></div>
	</div>
{/if}
