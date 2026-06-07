import { defineStore } from 'pinia'

export const categoryStore = defineStore('categoryStore', {
    state: () => ({
        classes: [],
        classnames: [],
        grades: [],
        specialties: [],
        users:[]
    }),
    actions: {
        addClass(category) {
            Array.prototype.push.apply(this.classes, category);
            // 根据需求决定是否需要复制对象
        },
        addClassName(category) {
            Array.prototype.push.apply(this.classnames, category); // 根据需求决定是否需要复制对象
        },
        addGrade(category) {
            Array.prototype.push.apply(this.grades, category); // 根据需求决定是否需要复制对象
        },
        addSpecialty(category) {
            Array.prototype.push.apply(this.specialties, category); // 根据需求决定是否需要复制对象
        },
    }
})