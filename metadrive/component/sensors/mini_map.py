from panda3d.core import Vec3

from metadrive.component.sensors.base_camera import BaseCamera
from metadrive.constants import CamMask
from metadrive.constants import DEFAULT_SENSOR_OFFSET, DEFAULT_SENSOR_HPR
from panda3d.core import FrameBufferProperties


class MiniMap(BaseCamera):
    CAM_MASK = CamMask.MiniMap
    TASK_NAME = "update_minimap_camera"

    def __init__(self, width, height, z_pos, engine, *, cuda=False):
        # 修复: 避免变量名混淆,使用明确的变量名
        self.BUFFER_W, self.BUFFER_H = width, height
        self.z_pos = z_pos  # 保存俯视高度
        super(MiniMap, self).__init__(engine=engine, need_cuda=cuda)

        cam = self.get_cam()
        lens = self.get_lens()

        # 初始化时先设置一个基本的俯视角度
        # 相机在z_pos高度,看向前方稍远的一点,形成俯视效果
        cam.setZ(z_pos)
        cam.lookAt(Vec3(0, 20, 0))
        lens.setAspectRatio(2.0)
        
        # 添加任务:每帧更新相机位置以跟踪agent
        self.engine.taskMgr.add(self._update_camera_task, self.TASK_NAME, sort=10)

    def _update_camera_task(self, task):
        """
        每帧更新相机位置,跟踪当前agent
        """
        if self.engine.current_track_agent is not None:
            agent = self.engine.current_track_agent
            # 将相机附加到agent
            if self.cam.getParent() != agent.origin:
                self.cam.reparentTo(agent.origin)
            
            # 每帧都更新位置和朝向,确保相机始终在agent上方俯视
            self.cam.setPos(0, 0, self.z_pos)
            # lookAt的第二个参数是相对于第一个参数(agent.origin)的位置
            # 设置相机看向agent前方20米处的地面
            self.cam.lookAt(agent.origin, Vec3(0, 20, 0))
        return task.cont

    def perceive(self, to_float=True, new_parent_node=None, position=None, hpr=None):
        """
        重写perceive方法,自动跟踪当前agent
        """
        # 如果没有指定parent node,则自动跟踪当前agent
        if new_parent_node is None and self.engine.current_track_agent is not None:
            new_parent_node = self.engine.current_track_agent.origin
            # 设置俯视位置: 在车辆上方z_pos高度,俯视向下
            position = (0, 0, self.z_pos)
            # 设置俯视角度: pitch=-90度表示垂直向下看
            hpr = (0, -90, 0)
        
        return super(MiniMap, self).perceive(to_float, new_parent_node, position, hpr)
    
    def destroy(self):
        """
        清理资源时移除更新任务
        """
        self.engine.taskMgr.remove(self.TASK_NAME)
        super(MiniMap, self).destroy()

