#
# Copyright (C) 2010 Red Hat, Inc.
#  Written by Ian Main <imain@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

require 'nokogiri'
require 'socket'

def condormatic_instance_create(task)

  begin
    instance = task.instance
    realm = instance.realm rescue nil

    job_name = "job_#{instance.name}_#{instance.id}"

    instance.condor_job_id = job_name
    instance.save!

    # I use the 2>&1 to get stderr and stdout together because popen3 does not support
    # the ability to get the exit value of the command in ruby 1.8.
    pipe = IO.popen("condor_submit 2>&1", "w+")
    pipe.puts "universe = grid\n"
    Rails.logger.info "universe = grid\n"
    pipe.puts "executable = #{job_name}\n"
    Rails.logger.info "executable = #{job_name}\n"

    resource = "grid_resource = dcloud $$(provider_url) $$(username) $$(password) $$(image_key) #{instance.name}"
    if realm != nil
      resource += " $$(realm_key)"
    else
      resource += " NULL"
    end
    resource += " $$(hardwareprofile_key) $$(keypair)\n"

    pipe.puts resource
    Rails.logger.info resource

    requirements = "requirements = hardwareprofile == \"#{instance.hardware_profile.id}\" && image == \"#{instance.template.id}\""
    requirements += " && realm == \"#{realm.id}\"" if realm != nil
    # We may need to add some stuff to the provider classads like pool id, provider id etc.  This is mostly just
    # to test and make sure this works for now.
    requirements += " && deltacloud_quota_check(\"#{job_name}\", other.cloud_account_id)"
    requirements += "\n"

    pipe.puts requirements
    Rails.logger.info requirements

    pipe.puts "notification = never\n"
    Rails.logger.info "notification = never\n"
    pipe.puts "queue\n"
    Rails.logger.info "queue\n"
    pipe.close_write
    out = pipe.read
    pipe.close

    Rails.logger.info "$? (return value?) is #{$?}"
    raise ("Error calling condor_submit: #{out}") if $? != 0

  rescue Exception => ex
    task.state = Task::STATE_FAILED
    Rails.logger.error ex.message
    Rails.logger.error ex.backtrace
  else
    # FIXME: We're kinda lying here.. we don't know the state for the task but I don't think that matters so much
    # as we are just going to use the 'task' table as a kind of audit log.
    task.state = Task::STATE_PENDING
  end
  task.instance.save!
end

# JobStatus for condor jobs:
#
# 0 Unexpanded  U
# 1 Idle        I
# 2 Running     R
# 3 Removed     X
# 4 Completed   C
# 5 Held        H
# 6 Submission_err  E
#

def condor_to_instance_state(state_val)
  case state_val
    when '0'
      return Instance::STATE_PENDING
    when '1'
      return Instance::STATE_PENDING
    when '2'
      return Instance::STATE_RUNNING
    when '3'
      return Instance::STATE_STOPPED
    when '4'
      return Instance::STATE_STOPPED
    when '5'
      return Instance::STATE_ERROR
    when '6'
      return Instance::STATE_CREATE_FAILED
  else
    return Instance::STATE_PENDING
  end
end

def condormatic_instance_stop(task)
    instance =  task.instance_of?(InstanceTask) ? task.instance : task

    Rails.logger.info("calling condor_rm -constraint 'Cmd == \"#{instance.condor_job_id}\"' 2>&1")
    pipe = IO.popen("condor_rm -constraint 'Cmd == \"#{instance.condor_job_id}\"' 2>&1")
    out = pipe.read
    pipe.close

    Rails.logger.info("condor_rm return status is #{$?}")
    Rails.logger.error("Error calling condor_rm (exit code #{$?}) on job: #{out}") if $? != 0
end

def condormatic_instance_reset_error(instance)

  condormatic_instance_stop(instance)
    Rails.logger.info("calling condor_rm -forcex -constraint 'Cmd == \"#{instance.condor_job_id}\"' 2>&1")
    pipe = IO.popen("condor_rm -forcex -constraint 'Cmd == \"#{instance.condor_job_id}\"' 2>&1")
    out = pipe.read
    pipe.close

    Rails.logger.info("condor_rm return status is #{$?}")
    Rails.logger.error("Error calling condor_rm (exit code #{$?}) on job: #{out}") if $? != 0
end

def condormatic_instance_destroy(task)
    instance = task.instance

    Rails.logger.info("calling condor_rm -constraint 'Cmd == \"#{instance.condor_job_id}\"' 2>&1")
    pipe = IO.popen("condor_rm -constraint 'Cmd == \"#{instance.condor_job_id}\"' 2>&1")
    out = pipe.read
    pipe.close

    Rails.logger.info("condor_rm return status is #{$?}")
    Rails.logger.error("Error calling condor_rm (exit code #{$?}) on job: #{out}") if $? != 0
end


def condormatic_classads_sync
  Rails.logger.info "Starting condormatic_classads_sync..."
  index = 0
  providers = Provider.find(:all)


  # we first need to invalidate old ADS
  # FIXME: this invalidates *all* ads, including those not really
  # related to deltacloud.  It would be best if we could find a
  # way to restrict the classads that we actually invalidate,
  # but it seems that the invalidate only matches against Name,
  # Machine, and SlotID.  Unfortunately classads don't seem to
  # have a regex match, so we can't regex match on Name.  My
  # attempts with Machine also failed, for unknown reasons.
  #
  # The other way we could go about invalidating the ones
  # we care about is with something like:
  #
  # condor_status -startd -f "%s\n" Name
  # 
  # which will show only the names of the startd classads.
  # Then we could do the regex matching in ruby, and iterate
  # through the provider_combination_* ones.  This is a bit
  # racy, though, so I'm more inclined to just invalidate
  # everything at present.
  Rails.logger.info "Starting classad invalidate..."
  begin
    pipe = IO.popen("condor_advertise INVALIDATE_STARTD_ADS 2>&1", "w+")
    pipe.puts 'MyType="Query"'
    pipe.puts 'TargetType="Machine"'
    pipe.close_write
    out = pipe.read
    pipe.close

    Rails.logger.info "Did invalidate, output is #{out}"

    if $? != 0
      Rails.logger.error "Unable to invalidate classads: #{out}"
      raise "Unable to invalidate classads, classad sync failed"
    end
  rescue Errno::EPIPE
    # if we failed to run condor_advertise, then in all likelihood condor isn't
    # installed or isn't running.  In that case, there can't be any old
    # classads, so we just go on
  end

  Rails.logger.info "Syncing classads.."
  providers.each do |provider|
    provider.cloud_accounts.each do |account|
      provider.replicated_images.each do |replicated_image|
        # The replicated image entry gets put in the database as soon as we ask
        # to have the image built, so we only want to generate classads for it if
        # it is ready to be used.  When ready it will have an image key assigned
        # to it.
        if replicated_image.provider_image_key != nil
          provider.hardware_profiles.each do |hwp|
            provider.realms.each do |realm|
              pipe = IO.popen("condor_advertise UPDATE_STARTD_AD 2>&1", "w+")

              pipe.puts "Name=\"provider_combination_#{index}\""
              pipe.puts 'MyType="Machine"'
              pipe.puts 'Requirements=true'
              pipe.puts "\n# Stuff needed to match:"
              pipe.puts "hardwareprofile=\"#{hwp.aggregator_hardware_profiles[0].id}\""
              pipe.puts "image=\"#{replicated_image.image.template.id}\""
              pipe.puts "realm=\"#{realm.frontend_realms[0].id}\""
              pipe.puts "\n# Backend info to complete this job:"
              pipe.puts "image_key=\"#{replicated_image.provider_image_key}\""
              pipe.puts "hardwareprofile_key=\"#{hwp.external_key}\""
              pipe.puts "realm_key=\"#{realm.external_key}\""
              pipe.puts "provider_url=\"#{account.provider.url}\""
              pipe.puts "username=\"#{account.username}\""
              pipe.puts "password=\"#{account.password}\""
              pipe.puts "cloud_account_id=\"#{account.id}\""
              pipe.puts "keypair=\"#{account.instance_key.name}\""
              pipe.close_write

              out = pipe.read
              pipe.close

              Rails.logger.error "Unable to submit condor classad: #{out}" if $? != 0

              index += 1
            end
          end
        end
      end
    end

    Rails.logger.info "done"
  end
end

def kick_condor
  begin
    socket = Socket.new(Socket::AF_INET, Socket::SOCK_DGRAM, 0)
    in_addr = Socket.pack_sockaddr_in(7890, 'localhost')
    socket.connect(in_addr)
    socket.write("kick")
    socket.close
  rescue
    # if any of the above failed, it's possible that the condor_refreshd
    # daemon is not running.  This is especially useful when running the
    # spec tests, since you don't necessarily want condor running in that
    # circumstance.
    # FIXME: there are a couple of problems with ignoring errors here.  The
    # first is that if this does actually fail, then it's unclear when in the
    # future we will update the classads next.  The second problem is that
    # if condor_refreshd died for some reason, but condor itself is running,
    # condor could be running with stale data.
  end
end
