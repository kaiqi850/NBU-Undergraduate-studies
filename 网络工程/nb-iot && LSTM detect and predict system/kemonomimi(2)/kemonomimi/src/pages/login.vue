<template>
	<v-container>
		<v-sheet class="pa-12" rounded color="#F7F7F7">
			<v-card class="mx-auto px-6 py-9" max-width="344" elevation="4">
				<template v-slot:title>
					用户登录
				</template>

				<v-form v-model="form" @submit.prevent="onSubmit">
					<v-text-field v-model="username" :readonly="loading" :rules="usernameRules" class="mb-2" label="账号" clearable>
						<template v-slot:prepend>
							<v-icon icon="mdi-account-circle"></v-icon>
						</template>
					</v-text-field>

					<v-text-field v-model="password" :readonly="loading" :rules="passwordRules" class="mb-2" label="密码" clearable type="password">
						<template v-slot:prepend>
							<v-icon icon="mdi-lock"></v-icon>
						</template>
					</v-text-field>

					<br>

					<v-btn :loading="loading" color="success" size="large" type="submit" variant="elevated" block>
						登录
					</v-btn>
				</v-form>
			</v-card>
		</v-sheet>

	</v-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue';

const router = useRouter();

const username = ref('');
const usernameRules = ref([
	value => {
		if (value?.length > 0) return true

		return '账号未输入'
	},
]);
const password = ref('');
const passwordRules = ref([
	value => {
		if (value?.length > 0) return true

		return '密码未输入'
	},
]);
const form = ref(false);
const loading = ref(false);

function onSubmit() {
	if (!form.value) return

	loading.value = true

	setTimeout(() => {
		loading.value = false;
		router.push('/');
		// router.push('/index');
	}, 1000)
}

</script>
