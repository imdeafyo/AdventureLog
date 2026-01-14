<script lang="ts">
	import type { MoneyValue } from '$lib/types';
	import { CURRENCY_OPTIONS } from '$lib/money';
	import { createEventDispatcher } from 'svelte';
	import CurrencyDropdown from './CurrencyDropdown.svelte';

	type Props = {
		label?: string;
		value: MoneyValue;
		currencyOptions?: string[];
		placeholder?: string;
		min?: number;
		step?: number;
	};

	export let label: string | undefined;
	export let value: MoneyValue;
	export let currencyOptions: string[] = CURRENCY_OPTIONS;
	export let placeholder = '0.00';
	export let min: number | undefined = 0;
	export let step: number | undefined = 0.01;

	const dispatch = createEventDispatcher<{ change: MoneyValue }>();
	const currencyId = `money-currency-${Math.random().toString(36).slice(2, 8)}`;

	function updateAmount(event: Event) {
		const target = event.target as HTMLInputElement;
		const amount = target.value === '' ? null : Number(target.value);
		const next: MoneyValue = {
			amount: Number.isNaN(amount) ? null : amount,
			currency: value.currency
		};
		dispatch('change', next);
	}

	function updateCurrency(event: CustomEvent<string | null>) {
		const next: MoneyValue = {
			amount: value.amount,
			currency: event.detail || null
		};
		dispatch('change', next);
	}

	function clearValue() {
		dispatch('change', { amount: null, currency: null });
	}
</script>

<div class="form-control">
	{#if label}
		<label class="label" for="money-input">
			<span class="label-text font-medium">{label}</span>
		</label>
	{/if}
	<div class="flex gap-3 flex-col sm:flex-row">
		<input
			id="money-input"
			type="number"
			class="input input-bordered bg-base-100/80 focus:bg-base-100 flex-1"
			{placeholder}
			bind:value={value.amount}
			{min}
			{step}
			on:input={updateAmount}
		/>
		<CurrencyDropdown
			id={currencyId}
			value={value.currency}
			options={currencyOptions}
			on:change={updateCurrency}
		/>
		<button type="button" class="btn btn-neutral-200" on:click={clearValue}> Clear </button>
	</div>
</div>
