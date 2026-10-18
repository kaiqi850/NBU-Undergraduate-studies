from decimal import Decimal


def calculate_dp(n):
    dp = [0] * (n + 1)
    dp[1] = Decimal(1)
    dp[2] = Decimal(2)
    dp[3] = Decimal(4)

    for i in range(4, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2] + dp[i - 3]

    return dp[n]


n = int(input())
result = calculate_dp(n)
print(result)