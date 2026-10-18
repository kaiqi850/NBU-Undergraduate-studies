(function (Vue) {
	
	const items=[
		{
			id:1,
			content:'vue.js',
			completed:false
		},
		{
			id:2,
			content:'java',
			completed:false
		},
		{
			id:3,
			content:'python',
			completed:false
		}
	]
	var app=new Vue({
		el:'#todoapp',
		data:{
			items,
			currentItem:null
		},
		computed:{
			toggleAll:{
				get:function () {
					return this.remaining===0
				},
				set(newStatus){
					this.items.forEach((item)=>{
						item.completed=newStatus
					})
				}

			},
			remaining(){
				return this.items.filter(item=>!item.completed).length	
			}
		},
		methods: {
			finishEdit(item,index,event){
				const content=event.target.value.trim();
				if (!content){
					this.removeItem(index)
					return
				}
				item.content=content
				this.currentItem=null
			},
			cancelEdit(){
				this.currentItem=null
			},
			toEdit(item){
				console.log(item)
				this.currentItem=item
			},
			removeCompleted(){
				this.items=this.items.filter(item=>!item.completed)
			},
			removeItem(index){
				this.items.splice(index,1)
			},
			additem(event){
				const content=event.target.value.trim()
				if (!content.length){

				}
				const id=this.items.length+1
				this.items.push({
					id,
					content,
					completed:false
				})
				event.target.value=''
			}
		} 
	})	 

})(Vue);
