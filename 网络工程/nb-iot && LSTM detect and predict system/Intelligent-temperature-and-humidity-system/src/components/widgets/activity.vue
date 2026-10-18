<script>
/**
 * Activity component
 */
export default {
  props: {
    title: {
      type: String,
      default: "Activity"
    },
    activityData: {
      type: Array,
      default: function() {
        return [];
      }
    }
  }
};
</script>

<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title mb-4">{{title}}</h4>
      <ol class="activity-feed">
        <li class="feed-item" v-for="activity in activityData" :key="activity.id">
          <div class="feed-item-list">
            <span class="date">{{activity.date}}</span>
            <span class="activity-text">{{activity.text}}</span>
          </div>
        </li>
      </ol>
      <div class="text-center">
        <a href="#" class="btn btn-primary">Load More</a>
      </div>
    </div>
    <!-- end card-body -->
  </div>
  <!-- end card -->
</template>