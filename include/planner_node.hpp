#ifndef PLANNER_H
#define PLANNER_H

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_msgs/msg/path.hpp"
#include "std_msgs/msg/empty.hpp"

namespace planner_node {

class DroneInfo
{
  std::string ns_;

  // Pose for takeoff and landing
  bool valid_landing_pose_;
  geometry_msgs::msg::PoseStamped landing_pose_;

  // At the moment, odometry is only used to capture the landing pad location
  // In the future the plan might be updated based on current drone locations
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

  // Publish a plan at 1Hz
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr plan_pub_;

  void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg);

public:

  explicit DroneInfo(rclcpp::Node *node, std::string ns);
  ~DroneInfo() {};

  std::string ns() const { return ns_; }
  bool valid_landing_pose() const { return valid_landing_pose_; }
  const geometry_msgs::msg::PoseStamped &landing_pose() const { return landing_pose_; }
  const rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr plan_pub() const { return plan_pub_; }
};

class PlannerNode : public rclcpp::Node
{
  // Global state
  bool mission_;

  // Arena runs from (0, 0, 0) to this point
  geometry_msgs::msg::Point arena_;

  // Per-drone info
  std::vector<std::shared_ptr<DroneInfo>> drones_;

  // Plans
  std::vector<nav_msgs::msg::Path> plans_;

  // Global subscriptions
  rclcpp::Subscription<std_msgs::msg::Empty>::SharedPtr start_mission_sub_;
  rclcpp::Subscription<std_msgs::msg::Empty>::SharedPtr stop_mission_sub_;

public:

  explicit PlannerNode();
  ~PlannerNode() {}

  void spin_once();

private:

  void spin_1Hz();

  void start_mission_callback(const std_msgs::msg::Empty::SharedPtr msg);
  void stop_mission_callback(const std_msgs::msg::Empty::SharedPtr msg);
};

} // namespace planner_node

#endif // PLANNER_H
