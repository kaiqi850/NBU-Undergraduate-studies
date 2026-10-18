#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>  // std::accumulate
#include <algorithm> // std::lower_bound, std::shuffle
#include <cassert>

// 随机数引擎
std::default_random_engine gen((unsigned)time(nullptr));

// 随机采样高斯分布
double sampleGaussian(double mean, double stddev) {
    std::normal_distribution<double> dist(mean, stddev);
    return dist(gen);
}

// 结构体：表示一个粒子（二维位置 + 朝向 + 权重）
struct Particle {
    double x;
    double y;
    double theta;   // 航向角，单位：弧度
    double weight;  // 归一化权重
};

// 隧道参数（示例：长 1000m，宽 10m，中心线为 x 方向）
constexpr double TUNNEL_LENGTH = 1000.0;   // 隧道长度（m）
constexpr double TUNNEL_WIDTH  = 10.0;     // 隧道宽度（m）
constexpr double TUNNEL_Y_MIN  = -TUNNEL_WIDTH / 2.0;
constexpr double TUNNEL_Y_MAX  =  TUNNEL_WIDTH / 2.0;

// 粒子滤波参数
constexpr int    N_PARTICLES   = 2000;         // 粒子数量
constexpr double SIGMA_ODOM_D  = 0.1;           // 里程计行驶距离噪声 (m)
constexpr double SIGMA_ODOM_TH = 0.0174533;     // 里程计转向噪声 (rad) ~1°
constexpr double SIGMA_LIDAR    = 0.2;          // LiDAR 测距噪声 (m)
constexpr double RESAMPLE_THRESH = N_PARTICLES / 2.0; // 有效粒子数阈值

// 全局粒子容器
std::vector<Particle> particles;

// 初始化粒子：假设车辆在隧道入口 (x=0, y=0, theta=0) 附近，小范围高斯分布
void initializeParticles() {
    std::normal_distribution<double> dist_x(0.0, 1.0);
    std::normal_distribution<double> dist_y(0.0, TUNNEL_WIDTH / 4.0);
    std::normal_distribution<double> dist_th(0.0, SIGMA_ODOM_TH * 5);

    particles.resize(N_PARTICLES);
    for (int i = 0; i < N_PARTICLES; i++) {
        particles[i].x     = dist_x(gen);
        particles[i].y     = dist_y(gen);
        particles[i].theta = dist_th(gen);
        particles[i].weight = 1.0 / N_PARTICLES;
    }
}

// 运动模型更新：对所有粒子应用里程计增量，并加入噪声
// delta_d：真是测量的行驶距离； delta_th：真实测量的航向变化
void motionUpdate(double delta_d, double delta_th) {
    for (auto &p : particles) {
        // 加噪声
        double noisy_d  = delta_d  + sampleGaussian(0.0, SIGMA_ODOM_D);
        double noisy_th = delta_th + sampleGaussian(0.0, SIGMA_ODOM_TH);

        // 简化 Ackermann 运动模型
        double prev_th = p.theta;
        p.x     += noisy_d * std::cos(prev_th + noisy_th / 2.0);
        p.y     += noisy_d * std::sin(prev_th + noisy_th / 2.0);
        p.theta += noisy_th;

        // 保持 theta 在 [-pi, +pi]
        if (p.theta > M_PI)       p.theta -= 2.0 * M_PI;
        else if (p.theta < -M_PI) p.theta += 2.0 * M_PI;

        // 如果粒子跑出隧道外，则将其权重置零
        if (p.x < 0.0 || p.x > TUNNEL_LENGTH ||
            p.y < TUNNEL_Y_MIN || p.y > TUNNEL_Y_MAX) {
            p.weight = 0.0;
        }
    }
}

// 简化测距模型：假设 LiDAR 只测车辆朝向正交左右两侧到隧道壁的垂直距离。
// lidar_measure[0]：测量车辆左侧到墙面的距离；
// lidar_measure[1]：测量车辆右侧到墙面的距离。
// 返回每个粒子的测距似然乘积（未归一化）
void measurementUpdate(const double lidar_measure[2]) {
    // 首先，所有粒子的权重乘以前一时刻的权重（保持原逻辑）
    // 然后计算新的观测似然
    double weight_sum = 0.0;
    for (auto &p : particles) {
        if (p.weight == 0.0) continue;  // 失效粒子略过

        // 计算粒子在隧道中对应的左右两侧到壁距离（几何推导）
        // 当粒子航向 theta = 0 时，左侧垂直方向就是 y 正方向
        // 因此，可以简单地认为：
        //   left_dist_hat  = (TUNNEL_WIDTH/2 - p.y) / |cos(theta)|
        //   right_dist_hat = (p.y + TUNNEL_WIDTH/2) / |cos(theta)|
        // 这里忽略了航向角对测距方向的影响，实际情况可用射线投射替换此处逻辑。
        double cos_th = std::abs(std::cos(p.theta));
        if (cos_th < 1e-6) {
            // 当 cos(theta) 过小时，粒子完全侧向朝向隧道壁，简化为极大距离
            p.weight = 0.0;
            continue;
        }
        double left_hat  = ( TUNNEL_Y_MAX - p.y ) / cos_th;  // y = +宽/2 的墙
        double right_hat = ( p.y - TUNNEL_Y_MIN ) / cos_th;  // y = -宽/2 的墙

        // 计算高斯似然
        double e_l = lidar_measure[0] - left_hat;
        double e_r = lidar_measure[1] - right_hat;
        double p_l = std::exp(- e_l * e_l / (2.0 * SIGMA_LIDAR * SIGMA_LIDAR));
        double p_r = std::exp(- e_r * e_r / (2.0 * SIGMA_LIDAR * SIGMA_LIDAR));

        // 更新权重
        p.weight = p.weight * (p_l * p_r);
        weight_sum += p.weight;
    }

    // 归一化权重
    if (weight_sum < 1e-15) {
        // 如果所有粒子权重都接近 0，重新初始化或均匀分布
        std::cerr << "Warning: All particle weights nearly zero. Reinitializing weights uniformly.\n";
        double uniform_w = 1.0 / N_PARTICLES;
        for (auto &p : particles) {
            p.weight = uniform_w;
        }
    } else {
        for (auto &p : particles) {
            p.weight /= weight_sum;
        }
    }
}

// 计算有效粒子数 N_eff = 1 / sum(w_i^2)
double computeEffectiveSampleSize() {
    double sum_sq = 0.0;
    for (auto &p : particles) {
        sum_sq += p.weight * p.weight;
    }
    if (sum_sq < 1e-15) return 0.0;
    return 1.0 / sum_sq;
}

// 低方差重采样（Low-variance Resampling）
void resampleParticles() {
    std::vector<Particle> new_particles;
    new_particles.reserve(N_PARTICLES);

    // 构造累积权重 CDF
    std::vector<double> cdf(N_PARTICLES);
    cdf[0] = particles[0].weight;
    for (int i = 1; i < N_PARTICLES; i++) {
        cdf[i] = cdf[i - 1] + particles[i].weight;
    }
    assert(std::abs(cdf.back() - 1.0) < 1e-6);  // 权重和应近似为 1

    // 随机初始起始点 u0 ~ Uniform[0, 1/N]
    std::uniform_real_distribution<double> uni_dist(0.0, 1.0 / N_PARTICLES);
    double u0 = uni_dist(gen);

    int idx = 0;
    for (int m = 0; m < N_PARTICLES; m++) {
        double u = u0 + double(m) / N_PARTICLES;
        // 在 cdf 中找到第一个 k 使得 cdf[k] >= u
        while (u > cdf[idx] && idx < N_PARTICLES - 1) {
            idx++;
        }
        // 复制该 idx 对应的粒子
        new_particles.push_back(particles[idx]);
        new_particles.back().weight = 1.0 / N_PARTICLES;
    }

    // 替换旧粒子集
    particles.swap(new_particles);
}

// 根据加权平均计算当前车体位姿估计
void estimatePose(double &est_x, double &est_y, double &est_theta) {
    est_x = 0.0;
    est_y = 0.0;
    double sin_sum = 0.0;
    double cos_sum = 0.0;

    for (auto &p : particles) {
        est_x    += p.weight * p.x;
        est_y    += p.weight * p.y;
        sin_sum  += p.weight * std::sin(p.theta);
        cos_sum  += p.weight * std::cos(p.theta);
    }
    est_theta = std::atan2(sin_sum, cos_sum);
}

// 模拟获取 LiDAR 左右测距（示例中的真实车辆 y=0，左右距离 = 宽/2 + 噪声）
// 在实际系统中，应由硬件或 API 获取
void getSimulatedLidar(double real_y, double lidar_measure[2]) {
    // 真实测距
    double true_left  = TUNNEL_Y_MAX - real_y;
    double true_right = real_y - TUNNEL_Y_MIN;

    // 加入噪声
    std::normal_distribution<double> dist_l(0.0, SIGMA_LIDAR);
    std::normal_distribution<double> dist_r(0.0, SIGMA_LIDAR);
    lidar_measure[0] = true_left  + dist_l(gen);
    lidar_measure[1] = true_right + dist_r(gen);
}

int main() {
    // 1. 初始化粒子
    initializeParticles();

    // 假设车辆真实状态（用于模拟测量），初始 (x=0, y=0, theta=0)
    double true_x = 0.0, true_y = 0.0, true_th = 0.0;

    // 仿真循环：假设车辆每步沿隧道中心线向前行驶 1m，共 100 步
    constexpr int STEPS = 100;
    for (int k = 0; k < STEPS; k++) {
        // === 1) 真实车辆运动（用于模拟测量） ===
        double real_delta_d  = 1.0;  // 向前行驶 1m
        double real_delta_th = 0.0;  // 保持直行
        true_x += real_delta_d * std::cos(true_th);
        true_y += real_delta_d * std::sin(true_th);
        true_th += real_delta_th;

        // === 2) 粒子运动预测 ===
        motionUpdate(real_delta_d, real_delta_th);

        // === 3) 模拟 LiDAR 测距 ===
        double lidar_measure[2] = {0.0, 0.0};
        getSimulatedLidar(true_y, lidar_measure);

        // === 4) 测量更新（加权） ===
        measurementUpdate(lidar_measure);

        // === 5) 计算 N_eff 并决定是否重采样 ===
        double N_eff = computeEffectiveSampleSize();
        if (N_eff < RESAMPLE_THRESH) {
            resampleParticles();
        }

        // === 6) 位姿估计 ===
        double est_x, est_y, est_th;
        estimatePose(est_x, est_y, est_th);

        // 输出每步的估计与真实值对比
        std::cout << "Step " << k
                  << " | True: (x=" << true_x << ", y=" << true_y << ", th=" << true_th << ")"
                  << " | Est: (x=" << est_x  << ", y=" << est_y  << ", th=" << est_th << ")"
                  << "\n";
    }

    return 0;
}

