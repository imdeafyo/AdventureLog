# Advanced Configuration

In addition to the primary configuration variables listed above, there are several optional environment variables that can be set to further customize your AdventureLog instance. These variables are not required for a basic setup but can enhance functionality and security.

| Name                         | Required | Description                                                                                                                                                                                | Default Value | Variable Location |
| ---------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- | ----------------- |
| `ACCOUNT_EMAIL_VERIFICATION` | No       | Enable email verification for new accounts. Options are `none`, `optional`, or `mandatory`                                                                                                 | `none`        | Backend           |
| `FORCE_SOCIALACCOUNT_LOGIN`  | No       | When set to `True`, only social login is allowed (no password login). The login page will show only social providers or redirect directly to the first provider if only one is configured. | `False`       | Backend           |
| `SOCIALACCOUNT_ALLOW_SIGNUP` | No       | When set to `True`, signup will be allowed via social providers even if registration is disabled.                                                                                          | `False`       | Backend           |
