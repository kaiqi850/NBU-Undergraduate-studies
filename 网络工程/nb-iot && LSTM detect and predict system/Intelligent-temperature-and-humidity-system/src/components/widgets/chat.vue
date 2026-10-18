<script>
import simplebar from "simplebar-vue";
import { required } from "vuelidate/lib/validators";

/**
 * Chat component
 */
export default {
  components: { simplebar },
  props: {
    title: {
      type: String,
      default: "Chat",
    },
    chatWindowHeight: {
      type: String,
      default: "367px",
    },
    chatMessages: {
      type: Array,
      default: function() {
        return [];
      },
    },
  },
  data() {
    return {
      chats: {
        message: "",
      },
      submitform: false,
    };
  },
  validations: {
    chats: {
      message: { required },
    },
  },
  methods: {
    /**
     * Chat form submit
     */
    saveMessage() {
      this.submitform = true;

      // stop here if form is invalid
      this.$v.$touch();
      if (this.$v.$invalid) {
        return;
      } else {
        var id = this.chatMessages.length;
        const message = this.chats.message;
        const currentDate = new Date();

        // Message Push in Chat
     this.chatMessages.push({
          image: require("@/assets/images/users/user-3.jpg"),
          id: id + 1,
          name: "Smith",
          message,
          odd: true,
          time: currentDate.getHours() + ":" + currentDate.getMinutes(),
        });
      }
      this.submitform = false;
      this.chats = {};
    },
  },
};
</script>

<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title mb-4">{{ title }}</h4>
      <div class="chat-conversation">
        <ul class="conversation-list">
          <simplebar :style="`max-height:${chatWindowHeight}`">
            <li
              v-for="chat in chatMessages"
              :key="chat.id"
              :class="{ odd: chat.odd === true }"
              class="clearfix"
            >
              <div class="chat-avatar">
                <img
                  :src="`${chat.image}`"
                  alt="male"
                  class="avatar-xs rounded-circle"
                />
                <span class="time">{{ chat.time }}</span>
              </div>
              <div class="conversation-text">
                <div class="ctext-wrap">
                  <span class="user-name">{{ chat.name }}</span>
                  <p>{{ chat.message }}</p>
                </div>
              </div>
            </li>
          </simplebar>
        </ul>
      </div>

      <form @submit.prevent="saveMessage">
        <div class="row pt-3">
          <div class="col-sm-9 col-8 chat-inputbar">
            <input
              id="message"
              v-model="chats.message"
              type="text"
              class="form-control chat-input"
              placeholder="Enter your text"
              name="message"
              :class="{ 'is-invalid': submitform && $v.chats.message.$error }"
            />
            <div
              v-if="submitform && !$v.chats.message.required"
              class="invalid-feedback"
            >
              This value is required.
            </div>
          </div>

          <div class="col-sm-3 col-4 chat-send">
            <div class="d-grid">
              <button type="submit" class="btn btn-success">Send</button>
            </div>
          </div>
        </div>
        <!-- end row -->
      </form>
      <!-- end form -->
    </div>
  </div>
</template>
